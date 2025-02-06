CONTAINER_NAME=meme-track
IMAGE_NAME=meme-track
VERSION=v0.2
PORT=6006

docker container stop $CONTAINER_NAME

docker container rm $CONTAINER_NAME


docker build -t $IMAGE_NAME:$VERSION .

docker run -d \
	--network="host"  \
	-p $PORT:$PORT \
	--name $CONTAINER_NAME  \
	$IMAGE_NAME:$VERSION \

echo "Container $CONTAINER_NAME started."
