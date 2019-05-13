var express = require("express"),
	app = express(),
	html = require("html"),
	bodyParser = require("body-parser");
var plotly = require("plotly")("", "");
var AWS = require("aws-sdk");



app.set("view engine", "ejs");
app.use(bodyParser.urlencoded({extended: true}));
app.use(bodyParser.json());
app.use(express.static(__dirname + '/'));


AWS.config.update({region: "us-east-1"});
AWS.config.credentials = new AWS.CognitoIdentityCredentials({
IdentityPoolId: "",
RoleArn: ""
});

var dynamodb = new AWS.DynamoDB();
var docClient = new AWS.DynamoDB.DocumentClient();

var TIME_INTERVAL = 5;


// read cat weight and plot
function weightPlot() {
	docClient.scan({TableName:"catFeed"}, function(err, data) {
	    if (err) {
	        console.error("Unable to read item. Error JSON:", JSON.stringify(err, null, 2));
	    } else {
	        // console.log("GetItem succeeded:", JSON.stringify(data, null, 2));
	        items = data["Items"];
	        items.sort(function(a,b){return -(a["time"]-b["time"])});
	        items = items.slice(0,6);
	        var x_val = [];
	        var y_val = [];
	        for (var i=0; i<items.length; i++)
	        {
	        	x_val.push(-i);
	        	y_val.push(items[i]["weight"]);
	        }
			var trace1 = {
			  x: x_val,
			  y: y_val,
			  type: "scatter"
			};
			var plotdata = [trace1];
			var graphOptions = {filename: "weight-chart", fileopt: "overwrite"};
			plotly.plot(plotdata, graphOptions, function (err, msg) {
			    console.log(msg);
			});
	    }
	});
};

// read catPosition and plot
function positionPlot() {
	docClient.scan({TableName:"catPosition"}, function(err, data) {
	    if (err) {
	        console.error("Unable to read item. Error JSON:", JSON.stringify(err, null, 2));
	    } else {
	        // console.log("GetItem succeeded:", JSON.stringify(data, null, 2));
	        items = data["Items"];
	        items.sort(function(a,b){return -(a["time"]-b["time"])});
	        var interval = 10;
	        var range = 10
	        for (var i=1; i<range && i*interval<items.length; i++)
	        	items[i] = items[i*interval];
	        items = items.slice(0,range);
	        var x_val = [];
	        var y_val = [];
	        for (var i=0; i<items.length; i++)
	        {
	        	x_val.push(items[i]["x"]/100);
	        	y_val.push(items[i]["y"]/100);
	        }
			var trace1 = {
			  x: x_val,
			  y: y_val,
			  type: "scatter"
			};
			var plotdata = [trace1];
			var graphOptions = {filename: "position-char", fileopt: "overwrite"};
			plotly.plot(plotdata, graphOptions, function (err, msg) {
			    console.log(msg);
			});
	    }
	});
};

positionPlot();
weightPlot();
setInterval(positionPlot, TIME_INTERVAL*2*1000);
setInterval(positionPlot, TIME_INTERVAL*2*1000);

app.get("/motion", (req, res) =>{
	console.log("cat motion");
	docClient.scan({TableName:"catFeed"}, function(err, data) {
	    if (err) {
	        console.error("Unable to read item. Error JSON:", JSON.stringify(err, null, 2));
	    } else {
	        // console.log("GetItem succeeded:", JSON.stringify(data, null, 2));
	        feed = data["Items"];
	        // grab the latest 5 record
	        feed.sort(function(a,b){return -(a["time"]-b["time"])});
	        feed = feed.slice(0,6);
			res.render("motion", {feed: feed, TIME_INTERVAL: TIME_INTERVAL});
	    }
	});
});




app.listen(process.env.PORT || 3000, process.env.IP, ()=>{
	console.log("server online!");
});


