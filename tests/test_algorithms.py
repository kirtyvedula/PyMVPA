#emacs: -*- mode: python-mode; py-indent-offset: 4; indent-tabs-mode: nil -*-
#ex: set sts=4 ts=4 sw=4 et:
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the PyMVPA package for the
#   copyright and license terms.
#
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
"""PyMVPA: Unit tests for PyMVPA pattern handling"""

import mvpa.algorithms as algorithms
import unittest
import numpy as N

class AlgorithmTests(unittest.TestCase):

    def testSphereGenerator(self):
        minimal = [ coords
            for center, coords in algorithms.SpheresInMask(
                    N.ones((1,1,1)), 1) ]

        # only one sphere possible
        self.failUnless( len(minimal) == 1 )
        # check sphere
        self.failUnless( minimal[0].shape == (1,1,1) )
        self.failUnless( minimal[0][0,0,0] == True )

        # make bigger 3d mask
        three_mask = N.ones((3,3,3))
        # disable a single voxel
        three_mask[1,1,1] = 0

        # get the spheres
        three = [ (center, spheremask.copy())
            for center, spheremask in algorithms.SpheresInMask(three_mask, 1) ]
        # check we have all but one
        self.failUnless( len(three) == 26 )

        # first sphere contains 4 voxels
        self.failUnless( three[0][1].sum() == 4 )

        # middle suface sphere contains one less (center voxel)
        self.failUnless( three[4][1].sum() == 5 )


        s = [ (c,sc.copy()) for c,sc in \
            algorithms.SpheresInMask( N.ones((2,2,2)),
                                      0.9,
                                      elementsize=(1,1,1),
                                      forcesphere=False ) ]
        # check for all possible sphere centers
        self.failUnless( len(s) == 8 )
        for coord in s:
            # center has to be in 3d
            self.failUnless( len(coord[0]) == 3 )
            # spheremask has to match mask size
            self.failUnless( coord[1].shape == (2,2,2) )
            # only one voxel must be in sphere
            self.failUnless( coord[1].sum() == 1 )
            # the sphere center is the only voxel
            self.failUnless( ( coord[0] == \
                             N.transpose( coord[1].nonzero())).all() )



def suite():
    return unittest.makeSuite(AlgorithmTests)


if __name__ == '__main__':
    unittest.main()

