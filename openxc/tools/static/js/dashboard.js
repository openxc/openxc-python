let dataPoints = {};

$(document).ready(function() {
    namespace = '';
    var socket = io(namespace);
    socket.on('vehicle data', function(msg, cb) {
        // console.log(msg);
        
        if (!(msg.name in dataPoints)) {
        	dataPoints[msg.name] = {
        		current_data: undefined,
        		events: {},
        		messages_received: 0,
        		measurement_type: undefined,
        		min: undefined,
        		max: undefined,
        		last_update_time: undefined,
        		average_time_since_update: undefined
        	};
        }

        updateDataPoint(dataPoints[msg.name], msg);
        updateDisplay(msg.name, msg.value);

        if (cb)
            cb();
    });
});

function addToDisplay(msgName) {
	$('<div/>', {
		id: msgName
	}).appendTo('#log');

	$('<span/>', {
		id: msgName + '_label',
		text: msgName + ': '
	}).appendTo('#' + msgName);

	$('<span/>', {
		id: msgName + '_value'
	}).appendTo('#' + msgName);
}

function updateDisplay(msgName, msgValue) {
	if (!($('#' + msgName).length > 0)) {
		addToDisplay(msgName);
	}

    $('#' + msgName + '_value').text(msgValue);
}

function updateDataPoint(dataPoint, measurement) {
	dataPoint.messages_received++;
	dataPoint.current_data = measurement;
	let update_time = (new Date()).getTime();

	if (dataPoint.last_update_time !== undefined) {
		dataPoint.average_time_since_update = 
			calculateAverageTimeSinceUpdate(update_time, dataPoint);
	}

	dataPoint.last_update_time = update_time;

	if ('event' in measurement) {
		dataPoint.events[measurement.value] = measurement.event;
	}
}

function calculateAverageTimeSinceUpdate(updateTime, dataPoint) {
	let time_since_update = updateTime - dataPoint.last_update_time;

	return (dataPoint.average_time_since_update === undefined) 
		? time_since_update
		: (0.1 * time_since_update) + (0.9 * dataPoint.average_time_since_update);
}