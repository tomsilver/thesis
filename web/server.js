var express = require('express');
var app = express();
var http = require('http').Server(app);
var io = require('socket.io')(http);

var nextUserID = 0;
var nextConvID = 0;
var unmatchedCompetitors = [];
var clients = {};
var conversations = {};

var Conversation = function (firstComp, secondComp, convID) {
  this.firstComp = firstComp;
  this.secondComp = secondComp;
  this.convID = convID;
  this.firstQuestions = [];
  this.secondQuestions = [];
  this.firstAnswers = [];
  this.secondAnswers = [];
};

Conversation.prototype.toJSONStr = function() {
  return JSON.stringify({'firstComp': this.firstComp, 'secondComp': this.secondComp});
};

Conversation.prototype.askQuestions = function(askerID, questions) {
  if (askerID == this.firstComp) {
  	this.firstQuestions = questions;
  	jsonQuestions = JSON.stringify({'questions': questions});
  	receiver = clients[this.secondComp];
  	receiver.emit('questions asked', jsonQuestions);
  }
  else {
  	this.secondQuestions = questions;
  	jsonQuestions = JSON.stringify({'questions': questions});
  	receiver = clients[this.firstComp];
  	receiver.emit('questions asked', jsonQuestions);
  }
};

Conversation.prototype.answerQuestions = function(answerID, answers) {
  if (answerID == this.firstComp) {
  	this.firstAnswers = answers;
  	jsonAnswers = JSON.stringify({'answers': answers});
  	receiver = clients[this.secondComp];
  	receiver.emit('answers given', jsonAnswers);
  }
  else {
  	this.secondAnswers = answers;
  	jsonAnswers = JSON.stringify({'answers': answers});
  	receiver = clients[this.firstComp];
  	receiver.emit('answers given', jsonAnswers);
  }
};

app.use(express.static(__dirname + '/public'));

io.on('connection', function(socket){
  thisID = nextUserID;
  socket.emit('id assignment', thisID);
  nextUserID += 1;
  clients[thisID] = socket;
  console.log("added client "+thisID.toString());
  socket.on('chat message', function(msg){
    io.emit('chat message', msg);
  });
  socket.on('match request', function(myID){
  	if (unmatchedCompetitors.length == 0){
  	  unmatchedCompetitors.push(myID);
  	}
  	else if (unmatchedCompetitors != [myID]){
	  comp = unmatchedCompetitors.shift();
	  conversation = new Conversation(myID, comp, nextConvID);
	  conversations[nextConvID] = conversation;
	  nextConvID += 1;
	  socket.emit('match set', conversation.convID);
	  clients[comp].emit('match set', conversation.convID);
  	}
  });
  socket.on('send questions', function(msg) {
  	jsonQuestions = JSON.parse(msg);
  	conv = conversations[jsonQuestions['conversationID']];
  	conv.askQuestions(jsonQuestions['userID'], jsonQuestions['questions']);
  });
  socket.on('send answers', function(msg) {
  	jsonQuestions = JSON.parse(msg);
  	conv = conversations[jsonQuestions['conversationID']];
  	conv.answerQuestions(jsonQuestions['userID'], jsonQuestions['answers']);
  });
  socket.on('disconnect', function() {
  	console.log("disconnected");
    delete clients[thisID];    
  });
});


http.listen(3000, function(){
  console.log('listening on *:3000');
});