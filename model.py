from keras.models import Sequential, load_model, Model
from keras.layers import Input, Dense, Conv2D, Flatten, BatchNormalization, Activation, LeakyReLU, add, ReLU
from keras.optimizers import SGD
from keras import regularizers

import keras.backend as K
import tensorflow as tf

import config

class Gen_Model():
    def __init__(self, reg_const, learning_rate, input_dim, output_dim):
        self.reg_const = reg_const
        self.learning_rate = learning_rate
        self.input_dim = input_dim
        self.output_dim = output_dim
        
    def softmax_cross_entropy_with_logits(self, y_true, y_pred):
        p = y_pred
        pi = y_true

        zero = tf.zeros(shape = tf.shape(pi), dtype=tf.float32)
        where = tf.equal(pi, zero)

        negatives = tf.fill(tf.shape(pi), -100.0) 
        p = tf.where(where, negatives, p)

        loss = tf.nn.softmax_cross_entropy_with_logits_v2(labels = pi, logits = p)

        return loss

    def predict(self, x):
        return self.model.predict(x)

    def fit(self, states, targets, epochs, verbose, validation_split, batch_size):
        return self.model.fit(states, targets, epochs=epochs, verbose=verbose, validation_split = validation_split, batch_size = batch_size)

    def write(self, version, type):
        self.model.save_weights(config.folder_agents + '\\' + "{0:0>5}".format(version) + type + '.h5')

    def read(self, version, type):
        return self.model.load_weights( config.folder_agents + '\\' + "{0:0>5}".format(version) + type + '.h5')

class Residual_CNN(Gen_Model):
    def __init__(self, reg_const, learning_rate, input_dim,  output_dim, hidden_layers):
        Gen_Model.__init__(self, reg_const, learning_rate, input_dim, output_dim)
        self.hidden_layers = hidden_layers
        self.num_layers = len(hidden_layers)
        self.model = self._build_model()

    def residual_layer(self, input_block, filters, kernel_size):
        x = self.conv_layer(input_block, filters, kernel_size)

        x = Conv2D(
        filters = filters
        , kernel_size = kernel_size
        , data_format="channels_first"
        , padding = 'same'
        , use_bias=False
        , activation='linear'
        , kernel_regularizer = regularizers.l2(self.reg_const)
        )(x)

        x = BatchNormalization(axis=1)(x)
        x = add([input_block, x])
        x = LeakyReLU()(x)

        return (x)

    def conv_layer(self, x, filters, kernel_size):
        x = Conv2D(
        filters = filters
        , kernel_size = kernel_size
        , data_format="channels_first"
        , padding = 'same'
        , use_bias=False
        , activation='linear'
        , kernel_regularizer = regularizers.l2(self.reg_const)
        )(x)

        x = BatchNormalization(axis=1)(x)
        x = LeakyReLU()(x)

        return (x)

    def value_head(self, x):
        x = Conv2D(
        filters = 16
        , kernel_size = (1,1)
        , data_format="channels_first"
        , padding = 'same'
        , use_bias=False
        , activation='linear'
        , kernel_regularizer = regularizers.l2(self.reg_const)
        , name = 'value_conv'
        )(x)


        x = BatchNormalization(axis=1, name='value_bn')(x)
        x = LeakyReLU(name='value_leaky_1')(x)
        x = Flatten(name='value_flatten')(x)

        x = Dense(
            50
            , use_bias=False
            , activation='linear'
            , kernel_regularizer=regularizers.l2(self.reg_const)
            , name = 'value_dense'
            )(x)

        x = LeakyReLU(name='value_leaky_2')(x)

        x = Dense(
            15
            , use_bias=False
            , activation='linear'
            , kernel_regularizer=regularizers.l2(self.reg_const)
            , name = 'value_dense_2'
            )(x)

        x = LeakyReLU(name='value_leaky_3')(x)

        x = Dense(
            1
            , use_bias=False
            , activation='tanh'
            , kernel_regularizer=regularizers.l2(self.reg_const)
            , name = 'value_head'
            )(x)

        return (x)

    def policy_head(self, x):
        x = Conv2D(
        filters = 2
        , kernel_size = (1,1)
        , data_format="channels_first"
        , padding = 'same'
        , use_bias=False
        , activation='linear'
        , kernel_regularizer = regularizers.l2(self.reg_const)
        , name = 'policy_conv'
        )(x)

        x = BatchNormalization(axis=1, name='policy_bn')(x)
        x = LeakyReLU(name='policy_leaky')(x)
        x = Flatten(name='policy_flatten')(x)

        x = Dense(
            self.output_dim
            , use_bias=False
            , activation='sigmoid'
            , kernel_regularizer=regularizers.l2(self.reg_const)
            , name = 'policy_head'
            )(x)

        return (x)

    def _build_model(self):
        main_input = Input(shape = self.input_dim, name = 'main_input')

        x = self.conv_layer(main_input, self.hidden_layers[0]['filters'], self.hidden_layers[0]['kernel_size'])

        if len(self.hidden_layers) > 1:
            for h in self.hidden_layers[1:]:
                x = self.residual_layer(x, h['filters'], h['kernel_size'])

        vh = self.value_head(x)
        #ph = self.policy_head(x)

        model = Model(inputs=[main_input], outputs=[vh])
        model.compile(loss={'value_head': 'mean_squared_error'},
            optimizer=SGD(lr=self.learning_rate, momentum = config.MOMENTUM),	
            #loss_weights={'value_head': 1.0}	
            )

        return model