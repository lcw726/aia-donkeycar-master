# Donkey Car
## 期末專題
## 2018技術領袖培訓班第二期

# 測試情境
1.      可以在全新車道上跑完五圈
2.      可以閃避在車道上的障礙物，如三角錐
3.      根據交通號誌/標誌做出相對反應(如左右轉、紅綠燈或斑馬線)

# Dataset
訓練資料其實很容易蒐集，拿搖桿控制車子跑上兩圈就有了。為了大家方便，我還是準備了一份
[訓練資料](https://drive.google.com/open?id=1jRC7PipqRdxmnjY-fjs_ickgdz9WoYtd)

# Label
每張影像檔都有對應的json描述檔


    {
        "user/mode": "user", 
        "user/angle": 1.0, 
        "user/throttle": 0.33919034394360176, 
        "cam/image_array": "1683_cam-image_array_.jpg", 
        "imu/accel_x": -0.0576171875, 
        "imu/accel_y": -0.105224609375, 
        "imu/accel_z": 1.135498046875, 
        "imu/gyro_x": 0.07548455893993378, 
        "imu/gyro_y": 0.02495477721095085, 
        "imu/gyro_z": 0.1672498732805252, 
        "imu/compass_x": -210.21829223632812, 
        "imu/compass_y": 257.4739685058594, 
        "imu/compass_z": -155.9217987060547, 
        "imu/pose_roll": 0.014761204831302166, 
        "imu/pose_pitch": 0.008595574647188187,
        "imu/pose_yaw": -2.2539045810699463,
        "timestamp": "2018-07-12T04:41:16.661911"
    }

其中user/angle是車子的方向，而user/throttle是車子的速度，這兩個值是model中的Y，其他的欄位可當作X使用。


[參考資料](https://drive.google.com/open?id=1bHA-pLjClAidSZAmeoTY520uZKVY1yL3ssD9TrxBp0Y)