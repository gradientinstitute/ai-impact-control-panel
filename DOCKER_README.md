
docker build . -f backend.Dockerfile -t minderoo_test 

docker run --rm -it -p 8666:8666 -v /home/lb/store/code/oversight-prototype/scenarios:/app/scenarios  minderoo_test
