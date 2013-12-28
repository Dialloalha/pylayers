#-*- coding:Utf-8 -*-
"""
Module : Cone

To facilitate algorithms implementation, the following conventions have been introduced. 
A Cone has an apex which is a point in the plane.
A cone has two vectors which define the cone aperture. 
Those two vectors can always been distinguished as a right vector (u) and a left vector (v).
The cone region is defined by the convex angular sector from right vector (u) to left vector (v) 
rotating folllowing the trigonometric convention.
The modulus of the cross product between u and v is positive.

u ^ v = alpha z with alpha > 0 

"""
import numpy as np
import shapely as shp
import matplotlib.pyplot as plt
import pylayers.util.geomutil as geu
from matplotlib.path import Path
import matplotlib.patches as patches
import pdb


class Cone(object):

    def __init__(self, a=np.array([1,0]), b = np.array([0,1]), apex=np.array([0, 0])):
        """
        a : np.array (,2)
                basis vector
        b : np.array (,2)        
        apex : np.array (,2)
        """
        self.apex = apex
        # normalizing vectors
        an = a/np.sqrt(np.dot(a,a))
        bn = b/np.sqrt(np.dot(b,b))
        #pdb.set_trace()
        if np.cross(an,bn) > 0:
            self.u = an
            self.v = bn
        else:  
            self.u = bn
            self.v = an
        
        # -1 < gamma < 1
        self.dot = np.dot(self.u,self.v)
        self.cross = np.cross(self.u,self.v)

        if self.cross<>0:
            self.degenerated = False
        else:
            self.degenerated = True    

    def belong_seg(self,pta,phe):
        """ test if segment belong to cone

        Parameters
        ----------

        pta : np.array (2xNseg)
        phe : np.array (2xNseg)

        Notes
        -----

        A segment belongs to the cone 

        + if not all termination points lie in the same side outside the cone.

        """
        # pta being left of segment 1
        blta = geu.isleft(self.seg1[:,0].reshape(2,1),self.seg1[:,1].reshape(2,1),pta)
        # phe being left of segment 2
        blhe = geu.isleft(self.seg1[:,0].reshape(2,1),self.seg1[:,1].reshape(2,1),phe)
        # segment candidate for being above segment 1
        bup = blta & blhe
        #pdb.set_trace()
        bo1,bo2 = self.outside_point(pta[:,bup])
        bo3,bo4 = self.outside_point(phe[:,bup])

        bin = ~((bo1&bo3)|(bo2&bo4))
        bup[bup] = bin

        return(bup)

    def outside_point(self,p):
        """
        """

        a = self.apex[:,np.newaxis]
        b = a + self.u.reshape(2,1) 
        c = a + self.v.reshape(2,1) 

        p0a0 = p[0,:]-a[0,:]
        p1a1 = p[1,:]-a[1,:]
        b1 = ((b[0,:]-a[0,:])* p1a1 - ((b[1,:]-a[1,:])* p0a0 ))>0
        b2 = ((c[0,:]-a[0,:])* p1a1 - ((c[1,:]-a[1,:])* p0a0 ))>0

        return(~b1 & ~b2 , b1 & b2) 

    def belong_point2(self,p):
        """
        """

        a = self.apex[:,np.newaxis]
        b = a + self.u.reshape(2,1)
        c = a + self.v.reshape(2,1)

        p1a1 = p[1,:]-a[1,:]
        p0a0 = p[0,:]-a[0,:]
        b1 = ((b[0,:]-a[0,:])* p1a1 - ((b[1,:]-a[1,:])* p0a0 ))>0
        b2 = ((c[0,:]-a[0,:])* p1a1 - ((c[1,:]-a[1,:])* p0a0 ))>0
        
        return(b1^b2)

    def belong_point(self, p):
        """ test if p belongs to Cone

        Parameters
        ----------

        p  : np.array (Ndim x Npoints)

        Returns
        -------

        b : np.array boolean (1xNpoints)

        """

        # Ndim x Npoints
        if not self.degenerated:
            pt  = p - self.apex[:,np.newaxis]
            #puv = np.sum(self.bv[:,:,np.newaxis]*pt[:,np.newaxis,:],axis=0)
        
            #alpha = puv[0,:]-self.gamma*puv[1,:] 
            #beta  = puv[1,:]-self.gamma*puv[0,:]
            pu = np.sum(self.u[:,np.newaxis]*pt,axis=0)
            pv = np.sum(self.v[:,np.newaxis]*pt,axis=0)

            alpha = pu-self.dot*pv
            beta  = pv-self.dot*pu

            b = (beta>0)&(alpha>0)
        else:
            a0 = self.seg0[:,0]
            b0 = self.seg0[:,1]

            if self.u[0]<>0:
                slope = self.u[1]/self.u[0]
                y0 = a0[1]-slope*a0[0]
                y1 = b0[1]-slope*b0[0]
                b = (p[1,:] > slope*p[0,:] + min(y0,y1) ) & (p[1,:]<slope*p[0,:]+max(y0,y1) ) 
            else:    
                b = (p[0,:] >  min(a0[0],b0[0]) ) & (p[0,:]< max(a0[0],b0[0]) )
        return(b)

    def above(self, p):
        bo1 = self.belong(p)
        pb = p[:,bo1]
        if self.v[1]<>0:
            slope1 = self.v[1]/self.v[0]
            b1 = self.v[1] - slope1*self.v[0]
            bo2 = pb[1,:] > slope1*pb[0,:]+b  
        else:
            bo2 = pb[1,:] > self.seg1[1,0]   
           
        return(bo1,bo2)    
        
    def from2segs(self,seg0,seg1):
        """ creates a Cone from 2 segments

        Parameters
        ----------

        seg0 : 2 x 2  (Ndim x Npoints)
        seg1 : 2 x 2 

        Notes
        -----

        The only way for the cone to be degenerated when built from two segments is when the two segments 
        are on the same line.


        """ 
        # bv : (4,1)


        self.seg0 = seg0
        self.seg1 = seg1

        a0 = seg0[:,0]
        b0 = seg0[:,1]
        a1 = seg1[:,0]
        b1 = seg1[:,1]

        # check segment orientation (crossing)
      
        if not (geu.ccw(a0,b0,b1) ^
                geu.ccw(b0,b1,a1) ):
            v0 = (b1 - a0)
            v1 = (a1 - b0)
            twisted = True
        else:    
            v0 = (a1 - a0)
            v1 = (b1 - b0)
            twisted = False
        
        v0n = v0/np.sqrt(np.dot(v0,v0))
        v1n = v1/np.sqrt(np.dot(v1,v1))

        if np.cross(v0n,v1n) > 0:
            self.u = v0n
            self.v = v1n
            inversion = False
        else:  
            self.u = v1n
            self.v = v0n
            inversion = True 
        
        if  (not twisted) & (not inversion) :
            #reverse seg1
            print "reverse seg1"
            self.seg1 = self.seg1[:,::-1]
        if (inversion) & (not twisted):
            #reverse seg0 
            print "reverse seg0"
            self.seg0 = self.seg0[:,::-1]
        if twisted & inversion:
            #reverse seg0 and seg1   
            print "reverse seg0"
            print "reverse seg1"
            self.seg0 = self.seg0[:,::-1]      
            self.seg1 = self.seg1[:,::-1]

        self.dot = np.dot(self.u,self.v)
        self.cross = np.cross(self.u,self.v)

        if self.cross < 1e-15:
            self.degenerated=True
        else:    
            a0u = np.dot(a0,self.u)
            a0v = np.dot(a0,self.v)
            b0u = np.dot(b0,self.u)
            b0v = np.dot(b0,self.v)

            kb  = ((b0v-a0v)-self.dot*(b0u-a0u))/(self.dot*self.dot-1)
            self.apex = b0 + kb*self.v

    def show(self, **kwargs):
        """ show cone 

        Parameters
        ----------

        length : float 

        """
        defaults = {'length': 25.}
        for k in defaults:
            if k not in kwargs:
                kwargs[k] = defaults[k]

        if 'seg1' not in self.__dict__:    
            verts = [tuple(self.apex),
                     tuple(self.apex + kwargs['length'] * self.u),
                     tuple(self.apex + kwargs['length'] * self.v),
                     tuple(self.apex)
                    ]
            codes = [Path.MOVETO,
                Path.LINETO,
                Path.LINETO,
                Path.CLOSEPOLY,
            ]

        else:
            a0 = self.seg0[:,0]
            b0 = self.seg0[:,1]
            a1 = self.seg1[:,0]
            b1 = self.seg1[:,1]

            if not(self.degenerated):
                #verts = [tuple(self.apex),
                #         tuple(a1),
                #         tuple(b1),
                #         tuple(self.apex)
                #        ]
                verts = [tuple(self.apex),
                     tuple(self.apex + kwargs['length'] * self.u),
                     tuple(self.apex + kwargs['length'] * self.v),
                     tuple(self.apex)
                    ]
                codes = [Path.MOVETO,
                Path.LINETO,
                Path.LINETO,
                Path.CLOSEPOLY,
                ]
            else:
                if (geu.ccw(a0,b0,b1) ^
                    geu.ccw(b0,b1,a1) ):
                    verts = [tuple(b0),
                             tuple(a1),
                             tuple(b1),
                             tuple(a0),
                             tuple(b0)
                        ]

                else:
                    verts = [tuple(b0),
                             tuple(b1),
                             tuple(a1),
                             tuple(a0),
                             tuple(b0)
                        ]

                codes = [Path.MOVETO,
                Path.LINETO,
                Path.LINETO,
                Path.LINETO,
                Path.CLOSEPOLY,
                ]


        

        path = Path(verts, codes)

        fig = plt.figure(figsize=(10,10))
        ax = fig.add_subplot(111)
        ax.plot([self.apex[0],self.apex[0]+kwargs['length']*self.u[0]],
                [self.apex[1],self.apex[1]+kwargs['length']*self.u[1]],lw=1,color='b')
        ax.plot([self.apex[0],self.apex[0]+kwargs['length']*self.v[0]],
                [self.apex[1],self.apex[1]+kwargs['length']*self.v[1]],lw=1,color='r')
        if 'seg1' in self.__dict__:
            ax.plot([a0[0],b0[0]],[a0[1],b0[1]],lw=2,color='b')
            ax.plot([a1[0],b1[0]],[a1[1],b1[1]],lw=2,color='r')
        patch = patches.PathPatch(path, facecolor='orange', lw=2, alpha=0.3)
        ax.add_patch(patch)
        ax.axis('equal')
        # ax.set_xlim(-2,2)
        # ax.set_ylim(-2,2)

        return(fig, ax)