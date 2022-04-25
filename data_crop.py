import numpy as np

# Crop image to 256*256
def crop_image(array):
    ori_x_dim = array.shape[0]
    ori_y_dim = array.shape[1]

    x_, y_ = array[:, :].nonzero()

    x1 = x_.min()
    x2 = x_.max()
    y1 = y_.min()
    y2 = y_.max()

    x_dim = x2 - x1
    y_dim = y2 - y1
    array_1 = array[x1:x2, y1:y2]

    return array_1, [x_dim, y_dim], [x1, x2], [y1, y2], [ori_x_dim, ori_y_dim]

def y_crop(y_dim, array, tar_size):
    # y_axis to 256
    if y_dim <= tar_size:          # expand
        mode = 'y_expand'
        c_y = y_dim // 2
        c_tar = tar_size // 2
        array_y = np.zeros([array.shape[0], tar_size])

        new_y1 = c_tar - c_y
        new_y2 = y_dim + new_y1
        array_y[:, new_y1: new_y2] = array  # 在y轴中，原始数据的位置点y坐标new_y1, new_y2

    else:                     # reduce
        mode = 'y_reduce'
        c_y = y_dim // 2
        c_tar = tar_size // 2

        new_y1 = c_y - c_tar
        new_y2 = 2 * c_y - new_y1     # 用2*c_y，而不是y_dim
        array_y = array[:,new_y1: new_y2]
    return array_y, [new_y1, new_y2], mode

def x_crop(x_dim, array, tar_size):
    arrays_x = []
    # x_axis to 256
    if x_dim <= tar_size:          # expand
        mode = 'x_expand'
        c_x = x_dim // 2
        c_tar = tar_size // 2
        array_x = np.zeros([tar_size, tar_size])

        new_x1 = c_tar - c_x
        new_x2 = x_dim + new_x1
        array_x[new_x1: new_x2, :] = array
        arrays_x.append(array_x)
        overlap = 0

    # reduce
    elif x_dim - tar_size <=50:     # 此处会导致一部分信息发生损失
        mode = 'x_reduce_0'
        c_x = x_dim // 2
        c_tar = tar_size // 2

        new_x1 = c_x - c_tar
        new_x2 = 2 * c_x - new_x1
        array_x = array[new_x1: new_x2, :]
        arrays_x.append(array_x)
        overlap = 0
    else:
        mode = 'x_reduce_1'
        new_x1 = 0
        new_x2 = 0
        arrays_x.append(array[:tar_size, :])
        overlap = 2 * tar_size - x_dim
        arrays_x.append(array[x_dim-tar_size:, :])
    return arrays_x, overlap, [new_x1, new_x2], mode

# Recover image to original size
def x_reco(mode, new_x, c_dim, overlap, arrays):
    if mode == 'x_expand':
        array = arrays[0]
        array_rx = array[new_x[0]: new_x[1], :]
    elif mode == 'x_reduce_0':
        array = arrays[0]
        array_rx = np.zeros([c_dim[0], array.shape[1]])
        array_rx[new_x[0]: new_x[1], :] = array
    else:
        array_0 = arrays[0]
        array_1 = arrays[1]
        array_rx = np.zeros([c_dim[0], array_0.shape[1]])
        array_rx[:array_0.shape[0] - overlap, :] = array_0[:array_0.shape[0] - overlap, :]
        array_rx[array_0.shape[0] - overlap:array_0.shape[0], :] = (array_0[array_0.shape[0] - overlap:array_0.shape[0], :] + array_1[:overlap, :]) * 0.5
        array_rx[array_0.shape[0]:, :] = array_1[overlap:, :]
    return array_rx

def y_reco(mode, new_y, c_dim, array):
    if mode == 'y_expand':
        array_ry = array[:, new_y[0]: new_y[1]]
    else:
        array_ry = np.zeros([array.shape[0], c_dim[1]])
        array_ry[:, new_y[0]: new_y[1]] = array
    return array_ry

def reco_image(array, ori_dim, m_x, m_y):
    array_new = np.zeros([ori_dim[0], ori_dim[1]])
    array_new[m_x[0]:m_x[1], m_y[0]:m_y[1]] = array
    return array_new
