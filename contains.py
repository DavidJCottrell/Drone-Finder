def contains(P,R):

    import numpy as np
    intercepts = 0

    r_origin = R
    r_end = np.array([np.max(P[:,0])+30,np.max(P[:,1])+30])
    r_direction = r_end - r_origin
    
    for i in range(len(P)):
        u_origin = P[i,:]
        u_direction = P[(i+1)%len(P),:] - u_origin
        Z = np.array([u_direction,-r_direction])
        intercept_len = np.linalg.pinv(Z.T).dot(r_origin - u_origin)
        if (((intercept_len[0]>0) & (intercept_len[0]<1)) and ((intercept_len[1]>0) & (intercept_len[1]<1))) == 1:
            intercepts += 1
    
    if intercepts%2 == 1:
        return True
    else:
        return False
