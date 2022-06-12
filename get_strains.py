import sys
import numpy as np
import cv2 as cv2
import seaborn as sns
import argparse
import json 

if __name__  == "__main__":
    parser = argparse.ArgumentParser(description='Get Displacements in a sequence of DIC images .')
    parser.add_argument('--image_path', required=True, metavar='<path>', type=str, help='The path to the images to be parsed')
    parser.add_argument('--log_path', required=True, metavar='<path>', type=str, help='The path to the log directory (where the data Area_of_interes.md is stored) and the results will be saved. ')

    args = parser.parse_args()
    log_path = args.log_path
    image_path = args.image_path


    times           = []
    file_names      = []
    pts_x_ll        = []
    pts_y_ll        = []

    pts_l = []
    indx_l = []
    pt_mat_x_list = []

# print("Reading positions from Positions.log in ", log_path)
# with open(log_path+r"/Positions.log") as f:
#     lines = f.readlines()
#     num_pt_x = int(lines[0].split(",")[0].split("=")[1])
#     num_pt_y = int(lines[0].split(",")[1].split("=")[1])

#     i = 2
#     while( i < len(lines)-1):
#         split = lines[i].split(",")
#         times.append(float(split[1]))
#         file_names.append(split[2].strip())
#         i += 1
#         data = lines[i].split("\t")
#         j = 0
#         pt_l = []
#         while(j < len(data)-1):
#             point = data[j].split(",")
#             x = point[0]
#             y = point[1]
#             j += 1
#             pt_l.append(np.array([float(x), float(y)]))
#         pts_l.append(np.array(pt_l))
#         i += 1





def compute_disp_and_remove_rigid_transform(p1, p2):
         A = []
         B = []
         removed_indices = []
         for i in range(len(p1)):
                    if np.isnan(p1[i][0]):
                             assert np.isnan(p1[i][0]) and np.isnan(p1[i][1]) and np.isnan(p2[i][0]) and np.isnan(p2[i][1])
                             removed_indices.append(i)
                    else:
                             A.append(p1[i])
                             B.append(p2[i])
         A = np.matrix(A)
         B =  np.matrix(B)
         assert len(A) == len(B)
         N = A.shape[0]; # total points

         centroid_A = np.mean(A, axis=0)
         centroid_B = np.mean(B, axis=0)

         # centre the points
         AA = np.matrix(A - np.tile(centroid_A, (N, 1)))
         BB = np.matrix(B - np.tile(centroid_B, (N, 1)))

         # dot is matrix multiplication for array
         H = np.transpose(AA) * BB
         U, S, Vt = np.linalg.svd(H)
         R = Vt.T * U.T

         # special reflection case
         if np.linalg.det(R) < 0:
                    print("Reflection detected")
                    Vt[2,:] *= -1
                    R = Vt.T * U.T

         n = len(A)
         T = -R*centroid_A.T + centroid_B.T
         A2 = (R*A.T) + np.tile(T, (1, n))
         A2 = np.array(A2.T)
         out = []
         j = 0
         for i in range(len(p1)):
                    if np.isnan(p1[i][0]):
                             out.append(p1[i])
                    else:
                             out.append(A2[j])
                             j = j + 1
         out = np.array(out)
         return compute_displacement(p2, out)



def compute_displacement(point, pointf):
        """To compute a displacement between two point arrays"""
        assert len(point)==len(pointf)
        values = []
        for i, pt0 in enumerate(point):
                pt1 = pointf[i]
                values.append((pt1[0]-pt0[0], pt1[1]-pt0[1]))
        return values


def compute_strain_field_cauchy(dx, dy, disp_x, disp_y):
        """Compute strain field from displacement thanks to numpy"""
        
        strain_xx, strain_xy = np.gradient(disp_x, dx, dy, edge_order=2)
        strain_yx, strain_yy = np.gradient(disp_y, dx, dy, edge_order=2)

        strain_xx = strain_xx + .5*(np.power(strain_xx,2) + np.power(strain_yx,2))
        strain_yy = strain_yy + .5*(np.power(strain_yy,2) + np.power(strain_xy,2))
        strain_xy = 0.5*(strain_xy + strain_yx + strain_xx*strain_xy + strain_yx*strain_yy)
        return strain_xx, strain_xy, strain_yy


def compute_strain_field_engineering(dx, dy, disp_x, disp_y):
        """Compute strain field from displacement thanks to numpy"""
        
        strain_xx, strain_xy = np.gradient(disp_x, dx, dy, edge_order=2)
        strain_yx, strain_yy = np.gradient(disp_y, dx, dy, edge_order=2)

        strain_xx = strain_xx
        strain_yy = strain_yy
        strain_xy = 0.5*(strain_xy + strain_yx)
        return strain_xx, strain_xy, strain_yy


def get_strains(strain_type, pts_l, file_names, times, num_pt_x, num_pt_y):

    strain_xx_mat_l = []
    strain_xy_mat_l = []
    strain_yy_mat_l = []
    pt_mat_x_list   = []
    pt_mat_y_list   = []
    strain_xx_max_l = []
    strain_xx_min_l = []


    d0x = 0
    d0y = 0
    for image_index in range(0, len(times)): #TODO: #p2 Why does this have to start at 1?

        print("Computing strain on image " + str(image_index) +  " of " + str(len(file_names)) + " image=(" + file_names[image_index], end=")\n")

        ptsx = np.array([p[0] for p in pts_l[image_index]]).reshape((num_pt_x, num_pt_y))
        ptsy = np.array([p[1] for p in pts_l[image_index]]).reshape((num_pt_x, num_pt_y))

        pt_mat_x_list.append(ptsx)
        pt_mat_y_list.append(ptsy)

        disp = compute_disp_and_remove_rigid_transform(pts_l[image_index], pts_l[0])
        
        dx = np.array([d[0] for d in disp])
        dy = np.array([d[1] for d in disp])
        if image_index == 0 :
            d0x = (pt_mat_x_list[0][-1][0] - pt_mat_x_list[0][0][0])/num_pt_x
            d0y = (pt_mat_x_list[0][-1][1] - pt_mat_x_list[0][0][1])/num_pt_y


        dx = np.array(dx).reshape((num_pt_x, num_pt_y))
        dy = np.array(dy).reshape((num_pt_x, num_pt_y))


        if strain_type == "cauchy":
            strain_xx, strain_xy, strain_yy = compute_strain_field_cauchy(d0x, d0y, dx, dy)
        if strain_type == "engineering":
            strain_xx, strain_xy, strain_yy = compute_strain_field_engineering(d0x, d0y, dx, dy)


        strain_xx_max = np.amax(strain_xx)
        strain_xx_min = np.amin(strain_xx)

        strain_xx_max_l.append(strain_xx_max)
        strain_xx_min_l.append(strain_xx_min)

        strain_xx_mat_l.append(strain_xx)
        strain_yy_mat_l.append(strain_yy)
        strain_xy_mat_l.append(strain_xy)

    return strain_xx_mat_l, strain_yy_mat_l, strain_xy_mat_l


# def mat_l_to_csv(mat):
#     retstr = ""
#     for row in range(0, len(mat)):
#         for col in range(0, len(mat[row])):
#             retstr += str(mat[row][col])
#             if col < len(mat[row])-1:
#                 retstr += ","
#         retstr += "\n"
#     return retstr



# with open(log_path+r"strains_xx.csv", "w") as f:
#     f.write("numpoints_x="+str(num_pt_x)+", numpoints_y="+str(num_pt_y)+"\n")
#     f.write("image num, time, image name\n")
#     for q in range(0, len(strain_xx_mat_l)):
#         jsonstr = mat_l_to_csv(strain_xx_mat_l[q].T)
#         f.write(str(str(q) + "," + str(times[q]) + "," +file_names[q] + "\n" + jsonstr + "\n"))
    

# with open(log_path+r"strains_xy.csv", "w") as f:
#     f.write("numpoints_x="+str(num_pt_x)+", numpoints_y="+str(num_pt_y)+"\n")
#     f.write("image num, time, image name\n")
#     for q in range(0, len(strain_xy_mat_l)):
#         jsonstr = mat_l_to_csv(strain_xy_mat_l[q].T)
#         f.write(str(str(q) + "," + str(times[q]) + "," +file_names[q] + "\n" + jsonstr + "\n"))

# with open(log_path+r"strains_yy.csv", "w") as f:
#     f.write("numpoints_x="+str(num_pt_x)+", numpoints_y="+str(num_pt_y)+"\n")
#     f.write("image num, time, image name\n")
#     for q in range(0, len(strain_yy_mat_l)):
#         jsonstr = mat_l_to_csv(strain_yy_mat_l[q].T)
#         f.write(str(str(q) + "," + str(times[q]) + "," +file_names[q] + "\n" + jsonstr + "\n"))
