FROM nikolaik/python-nodejs:python3.10-nodejs16
WORKDIR /app
COPY requirements.txt requirements.txt
# RUN apk update
# RUN apk add make automake gcc g++ subversion python3-dev
RUN pip3 install -r requirements.txt
COPY package.json package.json
RUN npm i
COPY . .
CMD ["npm","run","start"]