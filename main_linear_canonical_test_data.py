import torch
import torch.nn as nn
from datetime import datetime

from src.Simulations.Linear_sysmdl import SystemModel
from src.Simulations.utils import DataGen,set_seed
import src.Simulations.config as config
from src.Simulations.Linear_canonical.parameters import F, H, Q_structure, R_structure,\
   m, m1_0


from src.KalmanNet_nn import KalmanNetNN

from src.Pipeline_EKF import Pipeline_EKF 
import matplotlib.pyplot as plt

set_seed(42)

print(torch.cuda.is_available())
print("Pipeline Start")

################
### Get Time ###
################
today = datetime.today()
now = datetime.now()
strToday = today.strftime("%m.%d.%y")
strNow = now.strftime("%H:%M:%S")
strTime = strToday + "_" + strNow
print("Current Time =", strTime)
path_results = 'KNet/'

####################
### Design Model ###
####################
args = config.general_settings()

### dataset parameters ##################################################
args.N_E = 1000
args.N_CV = 100
args.N_T = 200
# init condition
args.randomInit_train = False
args.randomInit_cv = False
args.randomInit_test = False
if args.randomInit_train or args.randomInit_cv or args.randomInit_test:
   # you can modify initial variance
   args.variance = 1
   args.distribution = 'normal' # 'uniform' or 'normal'
   m2_0 = args.variance * torch.eye(m)
else: 
   # deterministic initial condition
   m2_0 = 0 * torch.eye(m) 
# sequence length
args.T = 100
args.T_test = 90
args.randomLength = False
if args.randomLength:# you can modify T_max and T_min 
   args.T_max = 1000
   args.T_min = 100
   # set T and T_test to T_max for convenience of batch calculation
   args.T = args.T_max 
   args.T_test = args.T_max
else:
   train_lengthMask = None
   cv_lengthMask = None
   test_lengthMask = None
# noise
r2 = torch.tensor([1])
vdB = -20 # ratio v=q2/r2
v = 10**(vdB/10)
q2 = torch.mul(v,r2)
print("1/r2 [dB]: ", 10 * torch.log10(1/r2[0]))
print("1/q2 [dB]: ", 10 * torch.log10(1/q2[0]))

### training parameters ##################################################
args.use_cuda =  False # use GPU or not
args.n_steps = 4000
args.n_batch = 30
args.lr = 1e-4
args.wd = 1e-3

if args.use_cuda:
   if torch.cuda.is_available():
      device = torch.device('cuda')
      print("Using GPU")
   else:
      raise Exception("No GPU found, please set args.use_cuda = False")
else:
   device = torch.device('cpu')
   print("Using CPU")

### True model ##################################################
Q = q2 * Q_structure
R = r2 * R_structure
sys_model = SystemModel(F, Q, H, R, args.T, args.T_test)
sys_model.InitSequence(m1_0, m2_0)
print("State Evolution Matrix:",F)
print("Observation Matrix:",H)

###################################
### Data Loader (Generate Data) ###
###################################
dataFolderName = 'src/Simulations/Linear_canonical/data' + '/'
dataFileName = '2x2_rq020_T100.pt'
print("Start Data Gen")
DataGen(args, sys_model, dataFolderName + dataFileName)
print("Data Load")
if args.randomLength:
   [train_input, train_target, cv_input, cv_target, test_input, test_target,train_init, cv_init, test_init, train_lengthMask,cv_lengthMask,test_lengthMask] = torch.load(dataFolderName + dataFileName, map_location=device)
else:
   [train_input, train_target, cv_input, cv_target, test_input, test_target,_,_,_] = torch.load(dataFolderName + dataFileName, map_location=device)

test_input= [[105.14699935913086, 107.7281084060669, 110.2542552947998, 112.53490859270096, 115.03778147697449, 144.97523880004883, 150.86875820159912, 150.67326068878174, 151.91993236541748, 153.42402267456055, 157.04486465454102, 166.96407318115234, 177.13187789916992, 181.52482223510742, 184.24212646484375, 185.54985427856445, 187.3533821105957, 188.00452995300293, 188.68260955810547, 190.13284301757812, 191.08143997192383, 192.91286087036133, 194.25014305114746, 195.7426242828369, 197.91734886169434, 200.28426933288574, 202.77695274353027, 205.1079978942871, 207.8032512664795, 208.80612182617188, 210.69183731079102, 212.49694442749023, 214.08699798583984, 216.47200775146484, 218.50572204589844, 221.16046524047852, 223.5312786102295, 226.3650722503662, 230.1666374206543, 237.1420783996582, 240.05922317504883, 244.19688034057617, 249.82374954223633, 252.47067260742188, 255.49235153198242, 258.9254608154297, 264.1758232116699, 266.06202697753906, 267.9156837463379, 270.8935317993164, 278.1417770385742, 281.36682510375977, 288.9070281982422, 292.93545150756836, 296.4671974182129, 301.4216995239258, 304.4973258972168, 310.9093894958496, 315.14777755737305, 324.2544059753418, 329.42780685424805, 332.66028594970703, 340.5466957092285, 358.46886444091797, 361.68902587890625, 369.09620666503906, 371.5445327758789, 378.47740936279297, 381.2789993286133, 384.74143981933594, 388.1579818725586, 389.47606658935547, 393.24547576904297, 402.21312713623047, 405.2168197631836, 411.9861755371094, 423.6441192626953, 426.56848907470703, 431.2361831665039, 433.7596740722656, 436.92372131347656, 438.6347961425781, 444.11570739746094, 449.85874938964844, 457.6323013305664, 461.6709747314453, 463.0690612792969, 464.95367431640625, 466.18162536621094, 468.83048248291016, 472.13624572753906, 478.49930572509766, 486.2142105102539, 494.41678619384766, 503.4572296142578, 510.3508834838867, 513.2839508056641, 519.8489990234375, 527.3116683959961], [235.01654052734375, 234.20668411254883, 233.98334884643555, 233.5360336303711, 234.75179290771484, 267.48291778564453, 277.4527931213379, 278.6659507751465, 279.2803421020508, 279.9975776672363, 279.9169387817383, 280.73698806762695, 283.31460189819336, 284.0369415283203, 285.61919021606445, 285.86348724365234, 285.12038803100586, 284.8386459350586, 284.35791778564453, 283.2729949951172, 282.2669143676758, 282.6131057739258, 281.8336067199707, 281.77241134643555, 282.0390930175781, 282.5468292236328, 281.9203338623047, 282.7104835510254, 283.5459976196289, 282.92727279663086, 282.8353157043457, 283.16492462158203, 284.0757522583008, 284.5573425292969, 284.79634857177734, 285.4446105957031, 285.9269790649414, 286.31700134277344, 287.0226020812988, 288.13412857055664, 288.5201301574707, 289.5221824645996, 286.89523696899414, 286.50209045410156, 286.0661163330078, 285.8045425415039, 286.78136444091797, 287.20447540283203, 287.67200469970703, 288.73018646240234, 291.3461608886719, 292.1846046447754, 295.3095703125, 298.0580749511719, 299.03174209594727, 300.3823585510254, 301.3008232116699, 301.38315200805664, 301.7953796386719, 303.7198028564453, 306.5922317504883, 307.6872444152832, 308.5671272277832, 312.77855682373047, 312.43304443359375, 313.80692291259766, 313.86995697021484, 313.278076171875, 313.20597076416016, 308.38300704956055, 305.943546295166, 304.9669952392578, 303.6557807922363, 303.88539123535156, 303.5116958618164, 303.8524932861328, 308.23209381103516, 307.62128829956055, 307.7897644042969, 307.9869689941406, 307.3868293762207, 306.68362045288086, 305.5436248779297, 307.15221405029297, 309.7188720703125, 309.52580642700195, 309.67428970336914, 307.5725975036621, 309.32470703125, 312.97350311279297, 314.6335220336914, 316.928955078125, 317.65967559814453, 316.7883834838867, 315.6442070007324, 315.7523880004883, 316.1649055480957, 315.9037322998047, 316.6752014160156]]

print("trainset size:",train_target.size())
print("cvset size:",cv_target.size())
print("testset size:",test_target.size())

########################################
### Evaluate Observation Noise Floor ###
########################################
loss_obs = nn.MSELoss(reduction='mean')
MSE_obs_linear_arr = torch.empty(args.N_T)# MSE [Linear]  
# for i in range(args.N_T):
#    MSE_obs_linear_arr[i] = loss_obs(test_input[i], test_target[i]).item()   
MSE_obs_linear_avg = torch.mean(MSE_obs_linear_arr)
MSE_obs_dB_avg = 10 * torch.log10(MSE_obs_linear_avg)

# Standard deviation
MSE_obs_linear_std = torch.std(MSE_obs_linear_arr, unbiased=True)

# Confidence interval
obs_std_dB = 10 * torch.log10(MSE_obs_linear_std + MSE_obs_linear_avg) - MSE_obs_dB_avg

print("Observation Noise Floor - MSE LOSS:", MSE_obs_dB_avg, "[dB]")
print("Observation Noise Floor - STD:", obs_std_dB, "[dB]")

##############################
### Evaluate Kalman Filter ###
##############################
# print("Evaluate Kalman Filter True")
# if args.randomInit_test:
#    [MSE_KF_linear_arr, MSE_KF_linear_avg, MSE_KF_dB_avg, KF_out] = KFTest(args, sys_model, test_input, test_target, randomInit = True, test_init=test_init, test_lengthMask=test_lengthMask)
# else: 
#    [MSE_KF_linear_arr, MSE_KF_linear_avg, MSE_KF_dB_avg, KF_out] = KFTest(args, sys_model, test_input, test_target, test_lengthMask=test_lengthMask)


##########################
### KalmanNet Pipeline ###
##########################

### KalmanNet with full info ##########################################################################################
# Build Neural Network
print("KalmanNet with full model info")
KalmanNet_model = KalmanNetNN()
KalmanNet_model.NNBuild(sys_model, args)
print("Number of trainable parameters for KalmanNet:",sum(p.numel() for p in KalmanNet_model.parameters() if p.requires_grad))
## Train Neural Network
KalmanNet_Pipeline = Pipeline_EKF(strTime, "KNet", "KalmanNet")
KalmanNet_Pipeline.setssModel(sys_model)
KalmanNet_Pipeline.setModel(KalmanNet_model)
KalmanNet_Pipeline.setTrainingParams(args)

test_case_ind=0
for t in range(sys_model.T_test):

   # print(test_input[test_case_ind][0][t:t+10])
   # print([[test_input[test_case_ind][0][t:t+10].detach().numpy(),test_input[test_case_ind][1][t:t+10].detach().numpy()]])
   input_tensor=torch.tensor([[test_input[0][0:t+1],test_input[1][0:t+1]]])
   knet_out = KalmanNet_Pipeline.NNTest_RealTime(sys_model,input_tensor , 'KNet/pipeline_KalmanNet.pt',t+1)
   plt.scatter(knet_out[test_case_ind][0][-1].detach().numpy(),knet_out[test_case_ind][1][-1].detach().numpy())

   # print(knet_out)

plt.plot(test_input[test_case_ind],test_input[1])
# [MSE_test_linear_arr, MSE_test_linear_avg, MSE_test_dB_avg,knet_out,RunTime] = KalmanNet_Pipeline.NNTest(sys_model, test_input, test_target, path_results,load_model=True,load_model_path='KNet/pipeline_KalmanNet.pt')
# print(knet_out[test_case_ind])
x=knet_out[test_case_ind][0].detach().numpy()
y=knet_out[test_case_ind][1].detach().numpy()
# plt.ylim(-20,20)
plt.plot(x,y)
# plt.ylim(0,500)
plt.show()
# print(MSE_test_linear_arr, MSE_test_linear_avg, MSE_test_dB_avg,knet_out,RunTime)

