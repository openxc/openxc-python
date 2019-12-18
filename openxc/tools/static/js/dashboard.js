let dataPoints = {};

/* --- Dashboard parameters ------- */
let justChangedHighlightDuration;
let recentlyChangedHighlightDuration;
/* --- End dashboard parameters --- */

$(document).ready(function() {
	updateDashboardParameters();

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
        updateDisplay(dataPoints[msg.name]);

        if (cb)
            cb();
    });
});

function updateDashboardParameters() {
	valueChangedTimer = Number($('#justChangedHighlightDuration').val());
	valueRecentlyChangedTimer = Number($('#recentlyChangedHighlightDuration').val());
}

function saveSettings(e) {
	e.preventDefault();
	updateDashboardParameters();
}

function addToDisplay(msgName) {
	// Insert new rows alphabetically
	var added = false;
	$('#log tr').each(function() {
		if (msgName < $(this).children('td:eq(0)').text()) {
			$('<tr/>', {
				id: msgName
			}).insertBefore($(this));
			added = true;
			return false;
		}
	});

	if (!added) {
		$('<tr/>', {
			id: msgName
		}).appendTo('#log');
	}

	$('<td/>', {
		id: msgName + '_label',
		text: msgName
	}).appendTo('#' + msgName);

	$('<td/>', {
		id: msgName + '_value'
	}).appendTo('#' + msgName);

	$('<td/>', {
		id: msgName + '_num',
		class: 'metric'
	}).appendTo('#' + msgName);

	$('<td/>', {
		id: msgName + '_freq',
		class: 'metric'
	}).appendTo('#' + msgName);
}

function updateDisplay(dataPoint) {
	msg = dataPoint.current_data
	
	if (!($('#' + msg.name).length > 0)) {
		addToDisplay(msg.name);
	}

    $('#' + msg.name + '_value').text(msg.value);
    highlightCell('#' + msg.name + '_value');

    $('#' + msg.name + '_num').text(dataPoint.messages_received);
    $('#' + msg.name + '_freq').text(Math.ceil(1 / dataPoint.average_time_since_update));
}

function highlightCell(cellId) {
	$(cellId).stop(true);
    $(cellId).css({'background': '#1338F0', 'color': 'white'});
    $(cellId).animate({backgroundColor: '#949494'}, valueChangedTimer, function() {
    	$(this).animate({backgroundColor: '#FFFFFF', color: 'black'}, valueRecentlyChangedTimer);
    });
}

function validateSettingsForm() {
	let valid = true;
	let errors = [];

	$('.error').each(function() {
		$(this).text('');
	});

	errors = validateTimerInput($('#justChangedHighlightDuration'), errors);
	errors = validateTimerInput($('#recentlyChangedHighlightDuration'), errors);

	if (errors.length > 0) {
		valid = false;
		errors.forEach(function(e) {
			$('#' + e.id + '_error').text(e.msg);
		});
	}

	return valid;
}

function validateTimerInput(input, errors) {
	let inputVal = input.val();
	
	if (isNaN(inputVal) || inputVal < 0) {
		errors.push({id: input[0].id, msg: 'Input must be a positive number'});
	}

	return errors;
}

function updateDataPoint(dataPoint, measurement) {
	dataPoint.messages_received++;
	dataPoint.current_data = measurement;
	let update_time = (new Date()).getTime() / 1000;

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