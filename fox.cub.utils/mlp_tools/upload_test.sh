MODEL_ID="5d3eaf07010fb18a18b10737"
TOURNAMENT="5d3eaf08010fb18a18b1073b"
MODEL_TYPE="scoreline"
FOX_CUB_HOST="http://0.0.0.0:8888/"

batch=200
inputs=5
epochs=50
labels=7
URL="$FOX_CUB_HOST/api/v1/model/train?batch=$batch&labels=$labels&epochs=$epochs&inputs=$inputs&type=$MODEL_TYPE&model_id=$MODEL_ID"

curl -X POST $URL \
    -F "file=@./out.csv" \
    -H "Content-Type: multipart/form-data"
exit