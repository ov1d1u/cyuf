var hide_timestamp = true;

function _append(element) {
  if ($('#typing').length) {
    $(element).insertBefore($('#typing'))
  } else {
    $('body').append(element)
  }
  $('html,body').clearQueue()
  $('html,body').animate({scrollTop: $('html,body').height()}, 500)
}

function show_timestamps(show) {
  if (show == 'true'){
    $('.timestamp').show()
    hide_timestamp = false
  } else {
    $('.timestamp').hide()
    hide_timestamp = true
  }
}

function add_info(text, image) {
  var div = $('<div></div>')
  div.attr('class', 'infobox')
  if (image) {
    text = '<img src="data:image/png;base64, ' + image + '" / alt="(*)"> ' + text
  }
  div.html(text)
  _append(div)
}

function message_in(sender, message, timestamp) {
  var div = $('<div></div>')
  div.attr('class', 'message message_in')
  
  var time = $('<span></span>')
  time.attr('class', 'timestamp')
  if (!hide_timestamp) time.show()
  if (timestamp) time.html(' (' + timestamp + ')')
  
  var sender_id = $('<span></span>')
  sender_id.attr('class', 'yahoo_id')
  sender_id.append(sender)
  sender_id.append(time)
  sender_id.append(': ')
  
  div.html(sender_id)
  div.append(message)
  
  _append(div)
}

function message_out(sender, message, timestamp) {
  var div = $('<div></div>')
  div.attr('class', 'message message_out')
  
  var time = $('<span></span>')
  time.attr('class', 'timestamp')
  if (!hide_timestamp) time.show()
  if (timestamp) time.html(' (' + timestamp + ')')
  
  var sender_id = $('<span></span>')
  sender_id.attr('class', 'yahoo_id')
  sender_id.append(sender)
  sender_id.append(time)
  sender_id.append(': ')
  
  div.html(sender_id)
  div.append(message)
  
  _append(div)
}

function start_typing(who) {
  if ($('#typing').length) {
    $('#typing').remove();
  }
  var div = $('<div></div>')
  div.attr('class', 'typing')
  div.attr('id', 'typing')
  div.html(who + ' is typing...')
  
  _append(div)
}

function stop_typing() {
  $('#typing').html('&nbsp;')
}