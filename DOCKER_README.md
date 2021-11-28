
docker build . -f backend.Dockerfile -t deva_backend

docker run --rm -it -p 8666:8666 -v /home/lb/store/code/oversight-prototype/scenarios/:/app/scenarios deva_backend
