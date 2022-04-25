from SimpleITK import ReadImage
from SimpleITK import GetArrayFromImage
from os import path as ospath
from data_crop import *
import torch

def pred(filePath, cktPath):
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    net = torch.load(cktPath, 'cpu')
    net.eval()

    image = ReadImage(filePath)
    array = GetArrayFromImage(image)
    array = array / 1614          # 归一化
    if (ospath.basename(filePath))[-3:] == 'dcm' or (ospath.basename(filePath))[-3:] == 'DCM':
        array = array[0, :, :]
    array_1, c_dim, m_x, m_y, ori_dim = crop_image(array[:,:])   # crop minmax of x and y
    array_y, new_y, mode_y = y_crop(c_dim[1], array_1, 256)   # resize y_axis to 256
    array_x, overlap, new_x, mode_x = x_crop(c_dim[0], array_y, 256)      # resize x_axis to 256

    outputs = [[], [], [], []]  # t1c, T1DIXONC, t2, ct_Mask
    for m in range(len(array_x)):
        src_one = array_x[m][np.newaxis, np.newaxis,...]
        src_one = torch.from_numpy(src_one)
        src_one = src_one.type(torch.FloatTensor)
        src_one = src_one.to(device)
        output = net(src_one)

        for n in range(len(outputs)):
            outputs[n].append(output[n][0, 0, :, :].detach().cpu())

    new_array = []  # t1c, T1DIXONC, t2, ct_Mask
    for k in range(len(outputs)):
        array_rx = x_reco(mode_x, new_x, c_dim, overlap, outputs[k])
        array_ry = y_reco(mode_y, new_y, c_dim, array_rx)
        array_new = reco_image(array_ry, ori_dim, m_x, m_y)
        new_array.append(array_new)

    t1c = new_array[0] * 1900
    T1DIXONC = new_array[1] * 1510
    t2 = new_array[2] * 1948
    ct_Mask = new_array[3] * 3524 - 1024

    return t1c, T1DIXONC, t2, ct_Mask
