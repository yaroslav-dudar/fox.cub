package fox.cub.net

import org.deeplearning4j.nn.conf.MultiLayerConfiguration
import org.deeplearning4j.nn.conf.NeuralNetConfiguration
import org.deeplearning4j.nn.weights.WeightInit
import org.deeplearning4j.nn.api.OptimizationAlgorithm
import org.deeplearning4j.nn.conf.layers.DenseLayer
import org.deeplearning4j.nn.conf.layers.OutputLayer
import org.deeplearning4j.nn.multilayer.MultiLayerNetwork
import org.deeplearning4j.datasets.datavec.RecordReaderDataSetIterator
import org.deeplearning4j.optimize.listeners.ScoreIterationListener
import org.deeplearning4j.eval.Evaluation
import org.deeplearning4j.util.ModelSerializer

import org.nd4j.linalg.learning.config.Adam
import org.nd4j.linalg.activations.Activation
import org.nd4j.linalg.lossfunctions.LossFunctions.LossFunction
import org.nd4j.linalg.factory.Nd4j
import org.nd4j.linalg.api.ndarray.INDArray

import org.datavec.api.util.ClassPathResource
import org.datavec.api.records.reader.impl.csv.CSVRecordReader
import org.datavec.api.split.FileSplit

import scala.collection.mutable.ArrayBuffer
import java.io.File
import java.nio.file.Paths

/**
 * MLP neural network model
*/
object MLPNet {

    val batchSize = 500
    val labelIndex = 0

    var models = scala.collection.mutable.Map[String, MultiLayerNetwork]()

    def buildNetworkConf(numLabels: Int, numInputs: Int): MultiLayerConfiguration = {
        val numHiddenNodes = numLabels * 4

        new NeuralNetConfiguration.Builder()
        .seed(12345)
        .updater(new Adam(0.01))
        .list()
        .layer(0, new DenseLayer.Builder().nIn(numInputs).nOut(numHiddenNodes)
                .weightInit(WeightInit.XAVIER)
                .activation(Activation.RELU)
                .build())
        .layer(1, new DenseLayer.Builder().nIn(numHiddenNodes).nOut(numHiddenNodes)
                .weightInit(WeightInit.XAVIER)
                .activation(Activation.RELU)
                .build())
        .layer(2, new OutputLayer.Builder(LossFunction.NEGATIVELOGLIKELIHOOD)
                .weightInit(WeightInit.XAVIER)
                .activation(Activation.SOFTMAX)
                .nIn(numHiddenNodes).nOut(numLabels).build())
        .backprop(true).pretrain(false)
        .build()
    }

    def trainModel(datasetPath: String,  modelName: String,
        numLabels: Int, numInputs: Int, nEpochs: Int = 30) {

         // Load the training data
        val reader = new CSVRecordReader();
        reader.initialize(new FileSplit(new File(datasetPath)))

        val trainIter = new RecordReaderDataSetIterator(
            reader,
            batchSize,
            labelIndex,
            numLabels)

        val model = new MultiLayerNetwork(buildNetworkConf(numLabels, numInputs))
        model.init()

        for ( n <- 0 to nEpochs) {
            model.fit(trainIter)
        }

        models += (modelName -> model)
    }

    def testModel(datasetPath: String, numLabels: Int, modelName: String) {
        //Load the test/evaluation data:
        val reader = new CSVRecordReader()
        reader.initialize(new FileSplit(new File(datasetPath)))

        val testIter = new RecordReaderDataSetIterator(
            reader,
            batchSize,
            labelIndex,
            numLabels)

        println("Evaluate model....");
        val eval = new Evaluation(numLabels);

        while(testIter.hasNext()){
            val t = testIter.next();
            val features = t.getFeatures();
            val lables = t.getLabels();
            val predicted = models(modelName).output(features,false);

            eval.eval(lables, predicted);

        }

        //Print the evaluation statistics
        println(eval.stats());
    }

    def predict(features: Array[Float], modelName: String) = {
        var score = models(modelName).output(Nd4j.create(features))
        score.getRow(0).data.asDouble.to[ArrayBuffer]
    }

    def loadModel(modelPath: String) {
        val modelName = Paths.get(modelPath).getFileName.toString
        models += (modelName -> ModelSerializer.restoreMultiLayerNetwork(modelPath, true))
    }

    def saveModel(modelPath: String, modelName: String) {
        ModelSerializer.writeModel(models(modelName), modelPath, true)
    }
}
