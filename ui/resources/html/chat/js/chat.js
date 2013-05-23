function _append(element) {
  if ($('#typing').length) {
    $(element).insertBefore($('#typing'))
  } else {
    $('body').append(element)
  }
  $('html,body').clearQueue()
  $('html,body').animate({scrollTop: $('html,body').height()}, 500)
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

function message_in(sender, message) {
  var div = $('<div></div>')
  div.attr('class', 'message message_in')
  
  var sender_id = $('<span></span>')
  sender_id.attr('class', 'yahoo_id')
  sender_id.html(sender + ': ')
  
  div.html(sender_id)
  div.append(message)
  
  _append(div)
}

function message_out(sender, message) {
  var div = $('<div></div>')
  div.attr('class', 'message message_out')
  
  var sender_id = $('<span></span>')
  sender_id.attr('class', 'yahoo_id')
  sender_id.html(sender + ': ')
  
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