# FSL-FINAL-PROJECT
objection detection using  few shot learning for indoor industiial applications
The dataset image can be downloaded from 

https://universityoflincoln-my.sharepoint.com/:f:/r/personal/25403914_students_lincoln_ac_uk/Documents/final%20research%20project/FINAL%20dataset/DATASET?csf=1&web=1&e=VKTjA0

The dataset with csv file to load for traditional classifier 

https://universityoflincoln-my.sharepoint.com/:f:/r/personal/25403914_students_lincoln_ac_uk/Documents/final%20research%20project/FINAL%20dataset/DATASET?csf=1&web=1&e=VKTjA0

The processed  dataset divided for train,test, and  validation For maml few shot learning can be found here. 

https://universityoflincoln-my.sharepoint.com/:f:/r/personal/25403914_students_lincoln_ac_uk/Documents/final%20research%20project/MAML/scripts/image_classification/customdataset?csf=1&web=1&e=EtqZUQ







# To run maml code

# training customdataset change N_way K_shot for training at different parameters(this below command is for 5 way 5 shot training)
python main.py --dataset=customdataset --mode=train --n_way=5 --k_shot=5 --k_query=15
# validation customdataset(for testing for 5 way 5 shot learning)
python main.py --dataset=customdataset --mode=test --n_way=5 --k_shot=5 --k_query=15

# history visualisation for train(to get all the metric graphs)
python history_vis.py --mode=train --n_way=5 --k_shot=15
# history visualisation for test
python history_vis.py --mode=test --n_way=5 --k_shot=15
