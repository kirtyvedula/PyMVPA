#emacs: -*- mode: python-mode; py-indent-offset: 4; indent-tabs-mode: nil -*-
#ex: set sts=4 ts=4 sw=4 et:
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the PyMVPA package for the
#   copyright and license terms.
#
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
"""PyMVPA: Recursive feature elimination"""

import numpy as N

from mvpa.misc.support import buildConfusionMatrix


class RFE( object ):
    """ Recursive feature elimination.
    """

    def __init__( self, pattern, clf ):
        """ Initialize recurse feature elimination
        """
        self.__pattern = pattern
        self.__verbose = False

        self.__clf = clf

        # train the classifier with the initial feature set
        self.__trainClassifier()


    def __trainClassifier(self):
        self.__clf.train( self.__pattern )
        self.__testClassifierOnTrainingSet()

        # feature rating: large values == important
        fr = self.__clf.getFeatureBenchmark()


    def __testClassifierOnTrainingSet(self):
        predictions = N.array(self.__clf.predict( self.pattern.samples ))

        self.__training_confusion_mat = \
            buildConfusionMatrix( self.pattern.reglabels,
                                  self.pattern.regs,
                                  predictions )
        self.__training_perf = \
            float(self.trainconfmat.diagonal().sum()) / self.trainconfmat.sum()


    def selectFeatures( self, n, eliminate_by = 'fraction',
                        kill_per_iter = 0.1 ):
        """ Select n predictive features from the dataset.

        This method performs as many iterations as necessary until only 'n'
        feature are remaining. The number of iteration depend on the elimination
        method that is used.

        'eliminate_by' and 'kill_per_iter' are used to determine how many
        features are removed in each iteration.

        Supported values for 'eliminate_by' and the associated meaning of
        'kill_per_iter' are listed below:

        eliminate_by: 'fraction'
            in this case 100*'kill_per_iter' represents the percentage of
            features that are removed at each iteration

        eliminate_by: 'number'
            each iteration removed 'number' features
        """
        # are we talking integers?
        n = int( n )

        # elimination log mask
        elim_mask = N.zeros( self.pattern.mapper.dsshape, dtype='uint' )

        # do it until there are more feature than there should be
        while n < self.pattern.nfeatures:
            # get importance of each remaining feature
            featrank = self.__clf.getFeatureBenchmark()

            # determine the number of features to be eliminated
            if eliminate_by == 'fraction':
                nkill = int( len(featrank) * kill_per_iter )
            elif eliminate_by == 'number':
                nkill = kill_per_iter
            else:
                raise ValueError, 'Unknown elimination method: ' \
                                  + str(eliminate_by)

            # limit number of eliminations if necessary (would have less than
            # n features after elimination)
            if nkill > self.pattern.nfeatures - n:
                nkill = self.pattern.nfeatures - n

            # make sure to remove one feature at least to prevent endless
            # loops
            if nkill < 1:
                nkill = 1

            if self.__verbose:
                print "Removing", nkill, "features.",

            # eliminate the first 'nkill' features (with the lowest ranking)
            self.__pattern = \
                self.pattern.selectFeatures( featrank.argsort()[nkill:] )

            # increment all features still present in the elim mask
            elim_mask[ self.pattern.mapper.getMask(copy=False) ] += 1

            # retrain the classifier with the new feature set
            self.__trainClassifier()

            if self.__verbose:
                print "New performance:", self.trainperf

        return elim_mask


    def killNFeatures( self, n,
                       eliminate_by = 'number',
                       kill_per_iter = 1 ):
        """ Eliminates the 'n' least predictive features.

        Please see the documentation of the selectFeatures() methods for
        information about the remaining arguments.
        """
        self.selectFeatures( self.pattern.nfeatures - n,
                             eliminate_by = eliminate_by,
                             kill_per_iter = kill_per_iter )


    def killFeatureFraction( self, frac,
                             eliminate_by = 'fraction',
                             kill_per_iter = 0.1 ):
        """ Eliminates the 100*frac percent least predictive features.

        Please see the documentation of the selectFeatures() methods for
        information about the remaining arguments.
        """
        nkill = int(frac * self.pattern.nfeatures)
        self.selectFeatures( self.pattern.nfeatures - nkill,
                             eliminate_by = eliminate_by,
                             kill_per_iter = kill_per_iter )


    def testSelection( self, pattern ):
        """ Test the performance of the current feature set on a given dataset.

        The datasets in 'pattern' (MVPAPattern) are passed to the internal
        classifier object. No retraining is performed. The classifiers
        predictions are compared to the regressor values in 'pattern'.

        'pattern' either has to provide the same number of features as the
        current feature set or has to match the original data shape. In case of
        the latter an automatic feature selection is performed and only those
        features from 'pattern' are used for the prediction that are also
        present in the current internal feature set.

        The method returns a 3-tuple:
            ( list of classifier prediction (one per dataset),
              mean classifier performance (0 < x < 1),
              confusion matrix of classifications )
        """
        if not pattern.nfeatures == self.pattern.nfeatures:
            # select necessary features from the provided patterns
            masked = pattern.selectFeaturesByMask( 
                            self.pattern.mapper.getMask() )
        else:
            masked = pattern

        # get the predictions from the classifier
        predicted = self.clf.predict( masked.samples )

        confmat = buildConfusionMatrix( self.pattern.reglabels,
                                        masked.regs,
                                        predicted )

        perf = N.mean( predicted == masked.regs )

        return predicted, perf, confmat


    def setVerbosity( self, value ):
        """ If verbosity is set to True, some status messages will be printed
        during recursive feature selection.
        """
        self.__verbose = value


    # properties
    pattern = property( fget=lambda self: self.__pattern )
    verbosity = property( fget=lambda self: self.__verbose,
                          fset=setVerbosity )
    clf = property( fget=lambda self: self.__clf )
    trainconfmat = property( fget=lambda self: self.__training_confusion_mat )
    trainperf = property( fget=lambda self: self.__training_perf )
