	var util = util || {};
	util.toArray = function(list) {
	  return Array.prototype.slice.call(list || [], 0);
	};
	var IP = '127.0.0.1'
var Terminal = Terminal || function(cmdLineContainer, outputContainer) {
	window.URL = window.URL || window.webkitURL;
	window.requestFileSystem = window.requestFileSystem || window.webkitRequestFileSystem;

	var cmdLine_ = document.querySelector(cmdLineContainer);
	var output_ = document.querySelector(outputContainer);

	const CMDS_ = ['/joinchat', '/leavechat', '/rsa', '/gfs', '/info', '/clear', '/pausescroll'];
	var fs_ = null;
	var cwd_ = null;    
	var history_ = [];
	var histpos_ = 0;
	var histtemp_ = 0;
	var header = '<div class=header id=myheader><img align="left" src="img/eye.png" width="100" height="100" style="padding: 0px 10px 20px 0px"><h2 style="letter-spacing: 4px">The Network</h2><p>' + '<p id="digitalclock">' + new Date() + '</p>' + '</p><p>Enter "/help" for more information.</p></div>'
	var chatinterval = null;
	var scrollpause = false;
	var ischatting = false;
	
	window.addEventListener('click', function(e) {
	cmdLine_.focus();
	}, false);

	cmdLine_.addEventListener('click', inputTextClick_, false);
	cmdLine_.addEventListener('keydown', historyHandler_, false);
	cmdLine_.addEventListener('keydown', processNewCommand_, false);

	function inputTextClick_(e)
	{
		this.value = this.value;
	}

	function historyHandler_(e) {
	if (history_.length) {
	  if (e.keyCode == 38 || e.keyCode == 40) {
		if (history_[histpos_]) {
		  history_[histpos_] = this.value;
		} else {
		  histtemp_ = this.value;
		}
	  }

	  if (e.keyCode == 38) { // up
		histpos_--;
		if (histpos_ < 0) {
		  histpos_ = 0;
		}
	  } else if (e.keyCode == 40) { // down
		histpos_++;
		if (histpos_ > history_.length) {
		  histpos_ = history_.length;
		}
	  }

	  if (e.keyCode == 38 || e.keyCode == 40) {
		this.value = history_[histpos_] ? history_[histpos_] : histtemp_;
		this.value = this.value; // Sets cursor to end of input.
	  }
	}
	}

	function processNewCommand_(e) {

	if (e.keyCode == 9) { // tab
	  e.preventDefault();
	  // Implement tab suggest.
	} else if (e.keyCode == 13) { // enter
	  // Save shell history.
	  if (this.value) {
		history_[history_.length] = this.value;
		histpos_ = history_.length;
	  }

	  // Duplicate current input and append to output section.
	  var line = this.parentNode.parentNode.cloneNode(true);
	  line.removeAttribute('id')
	  line.classList.add('line');
	  var input = line.querySelector('input.cmdline');
	  input.autofocus = false;
	  input.readOnly = true;
	  output_.appendChild(line);

	  if (this.value && this.value.trim()) {
		var args = this.value.split(' ').filter(function(val, i) {
		  return val;
		});
		var cmd = args[0].toLowerCase();
		args = args.splice(1); // Remove cmd from arg list.
	  }

	  switch (cmd) {
		case '/joinchat':
			if(ischatting)
			{
				output('You\'re already in the chat.')
			}
			else
			{
				ischatting = true
				output('You\'ve joined the chat.')
				chatinterval = setInterval(fetchmessages, 500);	
			}				  
			break;
		case '/leavechat':
			clearInterval(chatinterval);
			if(ischatting)
			{
				ischatting = false
				output('You\'ve left the chat.')
			}
			else
			{
				output('You want to leave something you\'re not in... weird.')
			}
			break;
		//case 'uname':
		  //output(navigator.appVersion);
		  //break;
		case '/rsa':
		  output('Information about rsa encryption and decryption goes here...');
		  break;
		case '/gfs':
		  output('Information about prime factorization system and new compression system goes here...');
		  break;
		case '/info':
		  output('Information about this app goes here...');
		  break;
		case '/pausescroll':
			if(scrollpause)
			{
				scrollpause = false
				output('Automatic scrolling resumed.')
			}
			else
			{
				scrollpause = true
				output('Automatic scrolling is paused, to enable again type /pausescroll again.')
			}
			break;
		case '/help':
			output('<div class="ls-files">' + CMDS_.join('<br>') + '</div>');
			output('/joinchat: join the chat of the network');
			output('/leavechat: leave the chat of the network');
			output('/rsa: info about RSA encryption and decryption');
			output('/gfs: info about prime factorization system and new compression system');
			output('/info: info about the app');
			output('/clear: clears the window');
			output('/pausescroll: pauses the automatic scrolling of text, reuse the same command to activate it again');
			break;
		case '/clear':
			output_.innerHTML = '';
			this.value = '';
			setHeader()
			return;
		default:
			if(ischatting && this.value)
			{
				broadcastmessage(this.value);
			}
			else if(cmd) 
			{
				output(cmd + ': command not found');
			}
	  };

	  //window.scrollTo(0, getDocHeight_());
	  this.value = ''; // Clear/setup line for next input.
	}}

	function formatColumns_(entries) {
	var maxName = entries[0].name;
	util.toArray(entries).forEach(function(entry, i) {
	  if (entry.name.length > maxName.length) {
		maxName = entry.name;
	  }
	});

	var height = entries.length <= 3 ?
		'height: ' + (entries.length * 15) + 'px;' : '';

	// 12px monospace font yields ~7px screen width.
	var colWidth = maxName.length * 7;

	return ['<div class="ls-files" style="-webkit-column-width:',
			colWidth, 'px;', height, '">'];
	}

	//
	function output(html) {
		output_.insertAdjacentHTML('beforeEnd', '<p>' + html + '</p>');
	}

	// Cross-browser impl to get document's height.
/* 	function getDocHeight_() {
	var d = document;
	return Math.max(
		Math.max(d.body.scrollHeight, d.documentElement.scrollHeight),
		Math.max(d.body.offsetHeight, d.documentElement.offsetHeight),
		Math.max(d.body.clientHeight, d.documentElement.clientHeight)
	);
	} */

	function digitalclocktick()
	{
		document.getElementById("digitalclock").innerHTML = new Date();	  
	}
	function setHeader()
	{
		output(header);
		setInterval(digitalclocktick, 1000);
	}

	function fetchmessages() {
		$.getJSON('/fetchmessages')
		.done(function(data)
		{
			mydata = JSON.parse(data)
			if(mydata != null)
			{
				output(`[${mydata.ip}][${mydata.timestamp.hour}:${mydata.timestamp.minute}:${mydata.timestamp.second}] # ${mydata.message}`);
			}
		})
		.fail(function(){
			clearInterval(chatinterval)
			ischatting = false
			output('You\'ve left the chat -> No connection with Network.py, is Network.py still running? [FETCH]');		
			});
	};
	function broadcastmessage(message){
		$.post('/broadcastmessage', {message: `${message}`, ip: `${IP}`}, "json")
		.done(function(data)
		{
			//console.log('success' + data);
		})
		.fail(function()
		{
			ischatting = false
			output('You\'ve left the chat -> No connection with Network.py, is Network.py still running? [BROADCAST]');
		});
	};
	
	//Return header and start clock
	setHeader();
	
	//Start scrolling methods
	const container = document.getElementById('container');
	container.addEventListener('DOMSubtreeModified', scrollToBottom);

	window.onscroll = function() {makeSticky()};
	var myheader = document.getElementById("myheader");
	var sticky = myheader.offsetTop;
	function makeSticky() {
	if (window.pageYOffset > sticky) {
		myheader.classList.add("sticky");
		} else {
		myheader.classList.remove("sticky");
		}
	}	
	function scrollToBottom() {
		if(!scrollpause)
		{
			window.scrollTo(0,document.body.scrollHeight);
		}
	}
	
/* 	return {
	init: function() {
	  output(header);
	  setInterval(digitalclocktick, 1000);	  
	},
	output: output
	} */
};

//Init
$('.prompt').html(`[${IP}] # `);
var term = new Terminal('#input-line .cmdline', '#container output');

	
  	
	
	