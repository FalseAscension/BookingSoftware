// Get Days of the week in given locale
function getWeekDays(locale)
{
    var baseDate = new Date(Date.UTC(2017, 0, 1)); // just a Sunday
    var weekDays = [];
    for(i = 0; i < 7; i++)
    {
        weekDays.push(baseDate.toLocaleDateString(locale, { weekday: 'long' }));
        baseDate.setDate(baseDate.getDate() + 1);
    }
    return weekDays;
}

// For generating the calendar interface as a HTML table.
function generateCalendar(daylist){
  var calendar = $("<div>").addClass("cal");
  var dayNames = getWeekDays("en-GB");

  var heads = $("<div>").addClass("chead");
  var days = $("<div>");

  $.each(daylist, function(i, d){
    heads.append($("<div>").addClass("citm").text(dayNames[d['day']]) );

    var day = $("<div>").addClass("cday").attr("id", "d" + d['day']);
    $.each(d['times'], function(i, time){
      day.append($("<div>").addClass("citm").attr("id", time).append($("<p>").text(time)))
    });
    days.append(day);

  });

  calendar.append(heads);
  calendar.append(days);

  return calendar;
}

function populateCalendar(cal, days, weekBeginning) {
  $.each(days, function(dIndex, d){
    var date = new Date();
    date.setDate(weekBeginning.getDate() + d['day']);
    $.ajax({
          type: "GET",
          url: "/api/getBookings",
          data: {date:date.toISOString().split("T")[0]},
          success: function(response) {
            $.each(response, function(bIndex, b){
              $(cal).find("#d" + d['day'] + " #" + b['time']).addClass("booked").attr("data-bookingid", b['bookingID']).text("Booked");
              console.log("#d" + d['day'] + " #" + b['time']);
            });
          }
    });
  });
}

function displayBooking(booking){
  return $("<div>").addClass("citm").text(booking["bookingID"]);
}

// Ensure all fields have been filled out and passwords match.
function validateForm(form) {
  var valid = true;

  // First check all fields have been filled out.
  $(form).children().each(function(i, inp) {
    if ($(inp).val() == '' | $(inp).attr('data-valid') == 'false')
      valid = false;
  });

  if(valid)
      $(`${form} input[type=submit]`).removeAttr('disabled');
  else
      $(`${form} input[type=submit]`).attr('disabled', 'disabled');

  return valid;
}

function ensurePasswordsMatch(form, p1, p2) {
  var match = false;

  if($(`${p1}`).val() == $(`${p2}`).val()) // passwords match.
    match = true;

  if(match) {
    $(`${p2}`).attr('data-valid', 'true');
  } else {
    $(`${p2}`).attr('data-valid', 'false');
  }

  return match;
}

// For creating a nicer JSON-string out of form values.
function formJSON(formArray) {
    var values = {};
    for(var i = 0; i < formArray.length; i++)
        values[formArray[i]['name']] = formArray[i]['value'];
    return JSON.stringify(values);
}
