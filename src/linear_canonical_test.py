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


class linear_canonical_test:
   def __init__(self):
      # set_seed(42)
      self.input_data=[[],[]]

      print(torch.cuda.is_available())
      print("Pipeline Start")

      ################
      ### Get Time ###
      ################
      today = datetime.today()
      now = datetime.now()
      strToday = today.strftime("%m.%d.%y")
      strNow = now.strftime("%H:%M:%S")
      self.strTime = strToday + "_" + strNow
      print("Current Time =", self.strTime)
      path_results = 'KNet/'

      ####################
      ### Design Model ###
      ####################
      self.args = config.general_settings()

      ### dataset parameters ##################################################
      self.args.N_E = 1000
      self.args.N_CV = 100
      self.args.N_T = 200
      # init condition
      self.args.randomInit_train = False
      self.args.randomInit_cv = False
      self.args.randomInit_test = False
      if self.args.randomInit_train or self.args.randomInit_cv or self.args.randomInit_test:
         # you can modify initial variance
         self.args.variance = 1
         self.args.distribution = 'normal' # 'uniform' or 'normal'
         m2_0 = self.args.variance * torch.eye(m)
      else: 
         # deterministic initial condition
         m2_0 = 0 * torch.eye(m) 
      # sequence length
      self.args.T = 100
      self.args.T_test = 10000
      self.args.randomLength = False
      if self.args.randomLength:# you can modify T_max and T_min 
         self.args.T_max = 1000
         self.args.T_min = 100
      # noise
      r2 = torch.tensor([1])
      vdB = -20 # ratio v=q2/r2
      v = 10**(vdB/10)
      q2 = torch.mul(v,r2)
      print("1/r2 [dB]: ", 10 * torch.log10(1/r2[0]))
      print("1/q2 [dB]: ", 10 * torch.log10(1/q2[0]))

      ### training parameters ##################################################
      self.args.use_cuda =  False # use GPU or not
      self.args.n_steps = 4000
      self.args.n_batch = 30
      self.args.lr = 1e-4
      self.args.wd = 1e-3
      if self.args.use_cuda:
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
      self.sys_model = SystemModel(F, Q, H, R, self.args.T, self.args.T_test)
      self.sys_model.InitSequence(m1_0, m2_0)
      print("State Evolution Matrix:",F)
      print("Observation Matrix:",H)
   def update(self,data):
      ###################################
      ### Data Loader (Generate Data) ###
      ###################################
      # dataFolderName = 'src/Simulations/Linear_canonical/data' + '/'
      # dataFileName = '2x2_rq020_T100.pt'
      # print("Start Data Gen")
      # DataGen(self.args, self.sys_model, dataFolderName + dataFileName)
      print("Data Load")
      self.input_data[0].append(data[0])
      self.input_data[1].append(data[1])
      # if self.args.randomLength:
      #    [train_input, train_target, cv_input, cv_target, test_input, test_target,train_init, cv_init, test_init, train_lengthMask,cv_lengthMask,test_lengthMask] = torch.load(dataFolderName + dataFileName, map_location=device)
      # else:
      #    [train_input, train_target, cv_input, cv_target, test_input, test_target,_,_,_] = torch.load(dataFolderName + dataFileName, map_location=device)

      # print("trainset size:",train_target.size())
      # print("cvset size:",cv_target.size())
      # print("testset size:",test_target.size())

      ########################################
      ### Evaluate Observation Noise Floor ###
      ########################################
      loss_obs = nn.MSELoss(reduction='mean')
      MSE_obs_linear_arr = torch.empty(self.args.N_T)# MSE [Linear]  
      # for i in range(self.args.N_T):
      #    MSE_obs_linear_arr[i] = loss_obs(test_input[i], test_target[i]).item()   
      MSE_obs_linear_avg = torch.mean(MSE_obs_linear_arr)
      MSE_obs_dB_avg = 10 * torch.log10(MSE_obs_linear_avg)

      # Standard deviation
      MSE_obs_linear_std = torch.std(MSE_obs_linear_arr, unbiased=True)

      # Conf+++++idence interval
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
      KalmanNet_model.NNBuild(self.sys_model, self.args)
      print("Number of trainable parameters for KalmanNet:",sum(p.numel() for p in KalmanNet_model.parameters() if p.requires_grad))
      ## Train Neural Network
      KalmanNet_Pipeline = Pipeline_EKF(self.strTime, "KNet", "KalmanNet")
      KalmanNet_Pipeline.setssModel(self.sys_model)
      KalmanNet_Pipeline.setModel(KalmanNet_model)
      KalmanNet_Pipeline.setTrainingParams(self.args)

      # test_case_ind=0
      # for t in range(self.sys_model.T_test):

         # print(test_input[test_case_ind][0][t:t+10])
         # print([[test_input[test_case_ind][0][t:t+10].detach().numpy(),test_input[test_case_ind][1][t:t+10].detach().numpy()]])
      # print("input:",self.input_data)
      input_tensor=torch.tensor([[self.input_data[0],self.input_data[1]]], dtype=torch.float)
      knet_out = KalmanNet_Pipeline.NNTest_RealTime(self.sys_model,input_tensor , 'KNet/pipeline_KalmanNet.pt',len(self.input_data[0]))
      # print(knet_out)
      return (knet_out[0][0][-1].detach().numpy(),knet_out[0][1][-1].detach().numpy())
         # plt.scatter(knet_out[test_case_ind][0][-1].detach().numpy(),knet_out[test_case_ind][1][-1].detach().numpy())

         # print(knet_out)

      # plt.plot(test_input[test_case_ind][0],test_input[test_case_ind][1])
      # [MSE_test_linear_arr, MSE_test_linear_avg, MSE_test_dB_avg,knet_out,RunTime] = KalmanNet_Pipeline.NNTest(sys_model, test_input, test_target, path_results,load_model=True,load_model_path='KNet/pipeline_KalmanNet.pt')
      # # print(knet_out[test_case_ind])
      # x=knet_out[test_case_ind][0].detach().numpy()
      # y=knet_out[test_case_ind][1].detach().numpy()
      # # plt.ylim(-20,20)
      # plt.plot(x,y)
      # plt.show()

      

# set_seed(42)

# print(torch.cuda.is_available())
# print("Pipeline Start")

# ################
# ### Get Time ###
# ################
# today = datetime.today()
# now = datetime.now()
# strToday = today.strftime("%m.%d.%y")
# strNow = now.strftime("%H:%M:%S")
# strTime = strToday + "_" + strNow
# print("Current Time =", strTime)
# path_results = 'KNet/'

# ####################
# ### Design Model ###
# ####################
# args = config.general_settings()

# ### dataset parameters ##################################################
# args.N_E = 1000
# args.N_CV = 100
# args.N_T = 200
# # init condition
# args.randomInit_train = False
# args.randomInit_cv = False
# args.randomInit_test = False
# if args.randomInit_train or args.randomInit_cv or args.randomInit_test:
#    # you can modify initial variance
#    args.variance = 1
#    args.distribution = 'normal' # 'uniform' or 'normal'
#    m2_0 = args.variance * torch.eye(m)
# else: 
#    # deterministic initial condition
#    m2_0 = 0 * torch.eye(m) 
# # sequence length
# args.T = 100
# args.T_test = 100
# args.randomLength = False
# if args.randomLength:# you can modify T_max and T_min 
#    args.T_max = 1000
#    args.T_min = 100
#    # set T and T_test to T_max for convenience of batch calculation
#    args.T = args.T_max 
#    args.T_test = args.T_max
# else:
#    train_lengthMask = None
#    cv_lengthMask = None
#    test_lengthMask = None
# # noise
# r2 = torch.tensor([1])
# vdB = -20 # ratio v=q2/r2
# v = 10**(vdB/10)
# q2 = torch.mul(v,r2)
# print("1/r2 [dB]: ", 10 * torch.log10(1/r2[0]))
# print("1/q2 [dB]: ", 10 * torch.log10(1/q2[0]))

# ### training parameters ##################################################
# args.use_cuda =  False # use GPU or not
# args.n_steps = 4000
# args.n_batch = 30
# args.lr = 1e-4
# args.wd = 1e-3

# if args.use_cuda:
#    if torch.cuda.is_available():
#       device = torch.device('cuda')
#       print("Using GPU")
#    else:
#       raise Exception("No GPU found, please set args.use_cuda = False")
# else:
#    device = torch.device('cpu')
#    print("Using CPU")

# ### True model ##################################################
# Q = q2 * Q_structure
# R = r2 * R_structure
# sys_model = SystemModel(F, Q, H, R, args.T, args.T_test)
# sys_model.InitSequence(m1_0, m2_0)
# print("State Evolution Matrix:",F)
# print("Observation Matrix:",H)

# ###################################
# ### Data Loader (Generate Data) ###
# ###################################
# dataFolderName = 'src/Simulations/Linear_canonical/data' + '/'
# dataFileName = '2x2_rq020_T100.pt'
# print("Start Data Gen")
# DataGen(args, sys_model, dataFolderName + dataFileName)
# print("Data Load")
# if args.randomLength:
#    [train_input, train_target, cv_input, cv_target, test_input, test_target,train_init, cv_init, test_init, train_lengthMask,cv_lengthMask,test_lengthMask] = torch.load(dataFolderName + dataFileName, map_location=device)
# else:
#    [train_input, train_target, cv_input, cv_target, test_input, test_target,_,_,_] = torch.load(dataFolderName + dataFileName, map_location=device)

# print("trainset size:",train_target.size())
# print("cvset size:",cv_target.size())
# print("testset size:",test_target.size())

# ########################################
# ### Evaluate Observation Noise Floor ###
# ########################################
# loss_obs = nn.MSELoss(reduction='mean')
# MSE_obs_linear_arr = torch.empty(args.N_T)# MSE [Linear]  
# for i in range(args.N_T):
#    MSE_obs_linear_arr[i] = loss_obs(test_input[i], test_target[i]).item()   
# MSE_obs_linear_avg = torch.mean(MSE_obs_linear_arr)
# MSE_obs_dB_avg = 10 * torch.log10(MSE_obs_linear_avg)

# # Standard deviation
# MSE_obs_linear_std = torch.std(MSE_obs_linear_arr, unbiased=True)

# # Confidence interval
# obs_std_dB = 10 * torch.log10(MSE_obs_linear_std + MSE_obs_linear_avg) - MSE_obs_dB_avg

# print("Observation Noise Floor - MSE LOSS:", MSE_obs_dB_avg, "[dB]")
# print("Observation Noise Floor - STD:", obs_std_dB, "[dB]")

# ##############################
# ### Evaluate Kalman Filter ###
# ##############################
# # print("Evaluate Kalman Filter True")
# # if args.randomInit_test:
# #    [MSE_KF_linear_arr, MSE_KF_linear_avg, MSE_KF_dB_avg, KF_out] = KFTest(args, sys_model, test_input, test_target, randomInit = True, test_init=test_init, test_lengthMask=test_lengthMask)
# # else: 
# #    [MSE_KF_linear_arr, MSE_KF_linear_avg, MSE_KF_dB_avg, KF_out] = KFTest(args, sys_model, test_input, test_target, test_lengthMask=test_lengthMask)


# ##########################
# ### KalmanNet Pipeline ###
# ##########################

# ### KalmanNet with full info ##########################################################################################
# # Build Neural Network
# print("KalmanNet with full model info")
# KalmanNet_model = KalmanNetNN()
# KalmanNet_model.NNBuild(sys_model, args)
# print("Number of trainable parameters for KalmanNet:",sum(p.numel() for p in KalmanNet_model.parameters() if p.requires_grad))
# ## Train Neural Network
# KalmanNet_Pipeline = Pipeline_EKF(strTime, "KNet", "KalmanNet")
# KalmanNet_Pipeline.setssModel(sys_model)
# KalmanNet_Pipeline.setModel(KalmanNet_model)
# KalmanNet_Pipeline.setTrainingParams(args)

# test_case_ind=0
# for t in range(sys_model.T_test):

#    # print(test_input[test_case_ind][0][t:t+10])
#    # print([[test_input[test_case_ind][0][t:t+10].detach().numpy(),test_input[test_case_ind][1][t:t+10].detach().numpy()]])
#    input_tensor=torch.tensor([[test_input[test_case_ind][0][0:t+1].detach().numpy(),test_input[test_case_ind][1][0:t+1].detach().numpy()]])
#    knet_out = KalmanNet_Pipeline.NNTest_RealTime(sys_model,input_tensor , 'KNet/pipeline_KalmanNet.pt',t+1)
#    plt.scatter(knet_out[test_case_ind][0][-1].detach().numpy(),knet_out[test_case_ind][1][-1].detach().numpy())

#    # print(knet_out)

# plt.plot(test_input[test_case_ind][0],test_input[test_case_ind][1])
# [MSE_test_linear_arr, MSE_test_linear_avg, MSE_test_dB_avg,knet_out,RunTime] = KalmanNet_Pipeline.NNTest(sys_model, test_input, test_target, path_results,load_model=True,load_model_path='KNet/pipeline_KalmanNet.pt')
# # print(knet_out[test_case_ind])
# x=knet_out[test_case_ind][0].detach().numpy()
# y=knet_out[test_case_ind][1].detach().numpy()
# # plt.ylim(-20,20)
# plt.plot(x,y)
# plt.show()
# # print(MSE_test_linear_arr, MSE_test_linear_avg, MSE_test_dB_avg,knet_out,RunTime)

