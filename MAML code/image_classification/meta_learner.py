"""Referenced from https://github.com/HilbertXu/MAML-Tensorflow
    Date: Feb 11st 2020
    Author: Hilbert XU
    Abstract: MetaLeaner model
"""
from task_generator import TaskGenerator

import tensorflow as tf
import tensorflow.keras as keras
import tensorflow.keras.backend as keras_backend
import os
import numpy as np 
import cv2

os.environ['CUDA_VISIBLE_DEVICES'] = '/gpu:0'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

def loss_fn(y, pred_y):
    '''
    :param pred_y: Prediction output of model
    :param y: Ground truth

    :return loss value:
    '''
    return tf.reduce_mean(tf.losses.categorical_crossentropy(y, pred_y))

class MetaLearner(tf.keras.models.Model):
    """
    Meta Learner
    """
    def __init__(self, args=None, bn=None):
        """
        :param filters: Number of filters in conv layers
        :param img_size: Size of input image, [84, 84, 3] 
        :param n_way: Number of classes
        :param name: Name of model
        """
        super(MetaLearner, self).__init__()
        # for miniimagener dataset set conv2d kernel size=[32, 3, 3]
        # for ominiglot dataset set conv2d kernel size=[64, 3, 3]
        if args is not None:
            if args.dataset == 'customdataset':
                self.filters = 32
                self.ip_size = (1, 84, 84, 3)
                self.op_channel = args.n_way    
                self.with_bn = args.with_bn
                self.training = True if args.mode is 'train' else False
            if args.dataset == 'omniglot':
                self.filters = 64
                self.ip_size = (1, 28, 28, 1)
                self.op_channel = args.n_way    
                self.with_bn = args.with_bn
                self.training = True if args.mode is 'train' else False
        else:
            self.filters = 32
            self.ip_size = (1, 84, 84, 3)
            self.op_channel = 5    
            self.training = True
            if bn is not None:
                self.with_bn     = bn
            else: 
                self.with_bn     = False

        if self.with_bn is True:
            # Build model layers
            self.conv_1 = tf.keras.layers.Conv2D(filters=self.filters, kernel_size=(3,3), strides=(1,1), padding='SAME', kernel_initializer='glorot_normal')
            self.bn_1 = tf.keras.layers.BatchNormalization(axis=-1)
            self.max_pool_1 = tf.keras.layers.MaxPool2D(pool_size=(2,2))

            self.conv_2 = tf.keras.layers.Conv2D(filters=self.filters, kernel_size=(3,3), strides=(1,1), padding='SAME', kernel_initializer='glorot_normal')
            self.bn_2 = tf.keras.layers.BatchNormalization(axis=-1)
            self.max_pool_2 = tf.keras.layers.MaxPool2D(pool_size=(2,2))

            self.conv_3 = tf.keras.layers.Conv2D(filters=self.filters, kernel_size=(3,3), strides=(1,1), padding='SAME', kernel_initializer='glorot_normal')
            self.bn_3 = tf.keras.layers.BatchNormalization(axis=-1)
            self.max_pool_3 = tf.keras.layers.MaxPool2D(pool_size=(2,2))

            self.conv_4 = tf.keras.layers.Conv2D(filters=self.filters, kernel_size=(3,3), strides=(1,1), padding='SAME', kernel_initializer='glorot_normal')
            self.bn_4 = tf.keras.layers.BatchNormalization(axis=-1)
            self.max_pool_4 = tf.keras.layers.MaxPool2D(pool_size=(2,2))

            self.fc = tf.keras.layers.Flatten()
            self.out = tf.keras.layers.Dense(self.op_channel)
        
        elif self.with_bn is False:
            self.conv_1 = tf.keras.layers.Conv2D(filters=self.filters, kernel_size=(3,3), strides=(1,1), padding='SAME', kernel_initializer='glorot_normal')
            self.max_pool_1 = tf.keras.layers.MaxPool2D(pool_size=(2,2))

            self.conv_2 = tf.keras.layers.Conv2D(filters=self.filters, kernel_size=(3,3), strides=(1,1), padding='SAME', kernel_initializer='glorot_normal')
            self.max_pool_2 = tf.keras.layers.MaxPool2D(pool_size=(2,2))

            self.conv_3 = tf.keras.layers.Conv2D(filters=self.filters, kernel_size=(3,3), strides=(1,1), padding='SAME', kernel_initializer='glorot_normal')
            self.max_pool_3 = tf.keras.layers.MaxPool2D(pool_size=(2,2))

            self.conv_4 = tf.keras.layers.Conv2D(filters=self.filters, kernel_size=(3,3), strides=(1,1), padding='SAME', kernel_initializer='glorot_normal')
            self.max_pool_4 = tf.keras.layers.MaxPool2D(pool_size=(2,2))

            self.fc = tf.keras.layers.Flatten()
            self.out = tf.keras.layers.Dense(self.op_channel)
    
    @property
    def inner_weights(self):
        '''
        :return model weights
        '''
        if self.with_bn is True:
            weights = [
                self.conv_1.kernel, self.conv_1.bias,
                self.bn_1.gamma, self.bn_1.beta,
                self.conv_2.kernel, self.conv_2.bias,
                self.bn_2.gamma, self.bn_2.beta,
                self.conv_3.kernel, self.conv_3.bias,
                self.bn_3.gamma, self.bn_3.beta,
                self.conv_4.kernel, self.conv_4.bias,
                self.bn_4.gamma, self.bn_4.beta,
                self.out.kernel, self.out.bias
            ]   
        elif self.with_bn is False:
            weights = [
                self.conv_1.kernel, self.conv_1.bias,
                self.conv_2.kernel, self.conv_2.bias,
                self.conv_3.kernel, self.conv_3.bias,
                self.conv_4.kernel, self.conv_4.bias,
                self.out.kernel, self.out.bias
            ]
        return weights

    @classmethod
    def initialize(cls, model):
        '''
        :return initialized model
        '''
        ip_size = model.ip_size
        model.build(ip_size)
        return model

    @classmethod
    def hard_copy(cls, model, args):
        copied_model = cls(args)
        copied_model.build(model.ip_size)

        if copied_model.with_bn is True:
            copied_model.conv_1.kernel = model.conv_1.kernel
            copied_model.conv_1.bias = model.conv_1.bias
            copied_model.bn_1.gamma = model.bn_1.gamma
            copied_model.bn_1.beta = model.bn_1.beta
            # copied_model.max_pool_1 = model.max_pool_1

            copied_model.conv_2.kernel = model.conv_2.kernel
            copied_model.conv_2.bias = model.conv_2.bias
            copied_model.bn_2.gamma = model.bn_2.gamma
            copied_model.bn_2.beta = model.bn_2.beta
            # copied_model.max_pool_2 = model.max_pool_2
            
            copied_model.conv_3.kernel = model.conv_3.kernel
            copied_model.conv_3.bias = model.conv_3.bias
            copied_model.bn_3.gamma = model.bn_3.gamma
            copied_model.bn_3.beta = model.bn_3.beta
            # copied_model.max_pool_3 = model.max_pool_3

            copied_model.conv_4.kernel = model.conv_4.kernel
            copied_model.conv_4.bias = model.conv_4.bias
            copied_model.bn_4.gamma = model.bn_4.gamma
            copied_model.bn_4.beta = model.bn_4.beta
            # copied_model.max_pool_4 = model.max_pool_4

            copied_model.out.kernel = model.out.kernel
            copied_model.out.bias = model.out.bias
            
        elif copied_model.with_bn is False:
            copied_model.conv_1.kernel = model.conv_1.kernel
            copied_model.conv_1.bias = model.conv_1.bias
            # copied_model.max_pool_1 = model.max_pool_1

            copied_model.conv_2.kernel = model.conv_2.kernel
            copied_model.conv_2.bias = model.conv_2.bias
            # copied_model.max_pool_2 = model.max_pool_2
            
            copied_model.conv_3.kernel = model.conv_3.kernel
            copied_model.conv_3.bias = model.conv_3.bias
            # copied_model.max_pool_3 = model.max_pool_3

            copied_model.conv_4.kernel = model.conv_4.kernel
            copied_model.conv_4.bias = model.conv_4.bias
            # copied_model.max_pool_4 = model.max_pool_4

            copied_model.out.kernel = model.out.kernel
            copied_model.out.bias = model.out.bias
        
        return copied_model

    
    @classmethod
    def meta_update(cls, model, args, alpha=0.01, grads=None):
        '''
        :param cls: Class MetaLearner
        :param model: Model to be copied
        :param alpah: The inner learning rate when update the fast weights
        :param grads: Gradients to generate fast weights
    
        :return model with fast weights
        '''
        # Make a hard copy of target model
        # If with bn layers, call like copied_model = cls(bn=True)
        copied_model = cls(args)
        '''
        !!!!!!!!!!!
        IMPORTANT
        !!!!!!!!!!!
        Must call copied_model.build(input_shape) to build up model weights before calling copied_model(x)
        If not, when we call copied_model(x) tf will reinitialize the model weights and overwrite the fast weights
        At the same time, GradientTape will fail to record it and the gradients will return Nones
        '''
        copied_model.build(model.ip_size)

        if copied_model.with_bn is True:
            copied_model.conv_1.kernel = model.conv_1.kernel
            copied_model.conv_1.bias = model.conv_1.bias
            copied_model.bn_1.gamma = model.bn_1.gamma
            copied_model.bn_1.beta = model.bn_1.beta
            # copied_model.max_pool_1 = model.max_pool_1

            copied_model.conv_2.kernel = model.conv_2.kernel
            copied_model.conv_2.bias = model.conv_2.bias
            copied_model.bn_2.gamma = model.bn_2.gamma
            copied_model.bn_2.beta = model.bn_2.beta
            # copied_model.max_pool_2 = model.max_pool_2
            
            copied_model.conv_3.kernel = model.conv_3.kernel
            copied_model.conv_3.bias = model.conv_3.bias
            copied_model.bn_3.gamma = model.bn_3.gamma
            copied_model.bn_3.beta = model.bn_3.beta
            # copied_model.max_pool_3 = model.max_pool_3

            copied_model.conv_4.kernel = model.conv_4.kernel
            copied_model.conv_4.bias = model.conv_4.bias
            copied_model.bn_4.gamma = model.bn_4.gamma
            copied_model.bn_4.beta = model.bn_4.beta
            # copied_model.max_pool_4 = model.max_pool_4

            copied_model.out.kernel = model.out.kernel
            copied_model.out.bias = model.out.bias

            # if call with gradients, apply it by using SGD
            # Manually apply Gradient descent as the task-level optimizer
            if grads is not None:
                copied_model.conv_1.kernel = copied_model.conv_1.kernel - alpha * grads[0]
                copied_model.conv_1.bias = copied_model.conv_1.bias - alpha * grads[1]
                copied_model.bn_1.gamma = copied_model.bn_1.gamma - alpha * grads[2]
                copied_model.bn_1.beta = copied_model.bn_1.beta - alpha * grads[3]

                copied_model.conv_2.kernel = copied_model.conv_2.kernel - alpha * grads[4]
                copied_model.conv_2.bias = copied_model.conv_2.bias - alpha * grads[5]
                copied_model.bn_2.gamma = copied_model.bn_2.gamma - alpha * grads[6]
                copied_model.bn_2.beta = copied_model.bn_2.beta - alpha * grads[7]

                copied_model.conv_3.kernel = copied_model.conv_3.kernel - alpha * grads[8]
                copied_model.conv_3.bias = copied_model.conv_3.bias - alpha * grads[9]
                copied_model.bn_3.gamma = copied_model.bn_3.gamma - alpha * grads[10]
                copied_model.bn_3.beta = copied_model.bn_3.beta - alpha * grads[11]

                copied_model.conv_4.kernel = copied_model.conv_4.kernel - alpha * grads[12]
                copied_model.conv_4.bias = copied_model.conv_4.bias - alpha * grads[13]
                copied_model.bn_4.gamma = copied_model.bn_4.gamma - alpha * grads[14]
                copied_model.bn_4.beta = copied_model.bn_4.beta - alpha * grads[15]

                copied_model.out.kernel = copied_model.out.kernel - alpha * grads[16]
                copied_model.out.bias = copied_model.out.bias - alpha * grads[17]

        elif copied_model.with_bn is False:
            copied_model.conv_1.kernel = model.conv_1.kernel
            copied_model.conv_1.bias = model.conv_1.bias
            # copied_model.max_pool_1 = model.max_pool_1

            copied_model.conv_2.kernel = model.conv_2.kernel
            copied_model.conv_2.bias = model.conv_2.bias
            # copied_model.max_pool_2 = model.max_pool_2
            
            copied_model.conv_3.kernel = model.conv_3.kernel
            copied_model.conv_3.bias = model.conv_3.bias
            # copied_model.max_pool_3 = model.max_pool_3

            copied_model.conv_4.kernel = model.conv_4.kernel
            copied_model.conv_4.bias = model.conv_4.bias
            # copied_model.max_pool_4 = model.max_pool_4

            copied_model.out.kernel = model.out.kernel
            copied_model.out.bias = model.out.bias

            # if call with gradients, apply it by using SGD
            # Manually apply Gradient descent as the task-level optimizer
            if grads is not None:
                copied_model.conv_1.kernel = copied_model.conv_1.kernel - alpha * grads[0]
                copied_model.conv_1.bias = copied_model.conv_1.bias - alpha * grads[1]

                copied_model.conv_2.kernel = copied_model.conv_2.kernel - alpha * grads[2]
                copied_model.conv_2.bias = copied_model.conv_2.bias - alpha * grads[3]

                copied_model.conv_3.kernel = copied_model.conv_3.kernel - alpha * grads[4]
                copied_model.conv_3.bias = copied_model.conv_3.bias - alpha * grads[5]

                copied_model.conv_4.kernel = copied_model.conv_4.kernel - alpha * grads[6]
                copied_model.conv_4.bias = copied_model.conv_4.bias - alpha * grads[7]

                copied_model.out.kernel = copied_model.out.kernel - alpha * grads[8]
                copied_model.out.bias = copied_model.out.bias - alpha * grads[9]
        
        return copied_model

    def call(self, x):
        '''
       
        '''
        if self.with_bn is True:
            # Conv block #1
            x = self.max_pool_1(tf.keras.activations.relu(self.bn_1(self.conv_1(x), training=self.training)))
            # Conv block #2
            x = self.max_pool_2(tf.keras.activations.relu(self.bn_2(self.conv_2(x), training=self.training)))
            # Conv block #3
            x = self.max_pool_3(tf.keras.activations.relu(self.bn_3(self.conv_3(x), training=self.training)))
            # Conv block #4
            x = self.max_pool_4(tf.keras.activations.relu(self.bn_4(self.conv_4(x), training=self.training)))
        
        elif self.with_bn is False:
            # Conv block #1
            x = self.max_pool_1(tf.keras.activations.relu(self.conv_1(x)))
            # Conv block #2
            x = self.max_pool_2(tf.keras.activations.relu(self.conv_2(x)))
            # Conv block #3
            x = self.max_pool_3(tf.keras.activations.relu(self.conv_3(x)))
            # Conv block #4
            x = self.max_pool_4(tf.keras.activations.relu(self.conv_4(x)))

        # Fully Connect Layer
        x = self.fc(x)
        # Logits Output
        logits = self.out(x)
        # Prediction
        pred = tf.keras.activations.softmax(logits)
        
        return logits, pred

