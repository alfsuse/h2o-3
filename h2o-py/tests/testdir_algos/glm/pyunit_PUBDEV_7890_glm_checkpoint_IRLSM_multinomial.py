from builtins import range
import sys
sys.path.insert(1,"../../../")
import h2o
from tests import pyunit_utils
from h2o.estimators.glm import H2OGeneralizedLinearEstimator

# check checkpointing for Multinomial with IRLSM.

def tesGLMtCheckpointing():
    print("Checking checkpoint for multinomials....")
    train = h2o.import_file(
        pyunit_utils.locate("smalldata/glm_test/multinomial_10_classes_10_cols_10000_Rows_train.csv"))
    train["C1"] = train["C1"].asfactor()
    train["C2"] = train["C2"].asfactor()
    train["C3"] = train["C3"].asfactor()
    train["C4"] = train["C4"].asfactor()
    train["C5"] = train["C5"].asfactor()
    train["C11"] = train["C11"].asfactor()
    myY = "C11"
    mX = list(range(0,10))
    buildModelCheckpointing(train, mX, myY, "multinomial") 

def buildModelCheckpointing(training_frame, x_indices, y_index, family):
    split_frames = training_frame.split_frame(ratios=[0.9], seed=12345)
    model = H2OGeneralizedLinearEstimator(family=family, max_iterations=3)
    model.train(training_frame=split_frames[0], x=x_indices, y=y_index, validation_frame=split_frames[1])
    modelCheckpoint = H2OGeneralizedLinearEstimator(family=family, checkpoint=model.model_id)
    modelCheckpoint.train(training_frame=split_frames[0], x=x_indices, y=y_index, validation_frame=split_frames[1])

    modelLong = H2OGeneralizedLinearEstimator(family=family) # allow to run to completion
    modelLong.train(training_frame=split_frames[0], x=x_indices, y=y_index, validation_frame=split_frames[1])
    
    checkpointCoef = modelCheckpoint.coef()
    longCoef = modelLong.coef()
    for key in longCoef.keys():
        pyunit_utils.assertEqualCoeffDicts(checkpointCoef[key], longCoef[key], tol=1e-6)


if __name__ == "__main__":
    h2o.init(ip="192.168.86.41", port=54321, strict_version_check=False)
    pyunit_utils.standalone_test(tesGLMtCheckpointing)
else:
    h2o.init(ip="192.168.86.41", port=54321, strict_version_check=False)
    tesGLMtCheckpointing()
