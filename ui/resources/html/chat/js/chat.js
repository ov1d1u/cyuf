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

function _createAudible(div, sender, url, message, timestamp) {
    var time = $('<span></span>')
    time.attr('class', 'timestamp')
    if (!hide_timestamp) time.show()
    if (timestamp) time.html(' (' + timestamp + ')')
    
    var sender_id = $('<span></span>')
    sender_id.attr('class', 'yahoo_id')
    sender_id.append('<span class="buddyname">' + sender + '</span>')
    sender_id.append(time)
    sender_id.append(': ')
    
    var swf_object = $('<div style="float:left;" class="audible_container"> \
    <object classid="clsid27cdb6e-ae6d-11cf-96b8-444553540000" id="audible_'+timestamp+'" width=100 height=100 \
    codebase="http://active.macromedia.com/flash2/cabs/swflash.cab#version=2,0,0,11"> \
    <param name="movie" value="'+url+'"> \
    <embed name="audible_'+timestamp+'" src="'+url+'" width="64" height="64" \
    pluginspage="http://www.macromedia.com/shockwave/download/index.cgi?p1_prod_version=shockwaveflash"> \
    </object></div>')
    
    div.html(sender_id)
    div.append('<br/>')
    div.append(swf_object)
    div.append('<div class="audible_message">' + message + '</div>')
    _append(div)
    
    var interval;
    
    var autoPlay = function() {
        try {
            clearInterval(interval);
            if (document.getElementsByName('audible_'+timestamp)[0].PercentLoaded() == 100){
                document.getElementsByName('audible_'+timestamp)[0].Play();
            } else {
                throw 'Not ready'
            }
        } catch(err) {
            clearInterval(interval);
            interval = setInterval(autoPlay, 100);
        }
    }
    
    autoPlay()
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

function update_buddy_name(name) {
    $('.buddyname').html(name)
    $('.message_in .buddyname').html(name)
}

function status_updated(text, image, timestamp) {
    $('#statusbox').remove()
    var div = $('<div></div>')
    div.attr('id', 'statusbox')
    if (image) {
        text = '<img src="data:image/png;base64, ' + image + '" / alt="(*)"> <b>' + text + '</b> (' + timestamp + ')'
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
  sender_id.append('<span class="buddyname">' + sender + '</span>')
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
  sender_id.append('<span class="buddyname">' + sender + '</span>')
  sender_id.append(time)
  sender_id.append(': ')
  
  div.html(sender_id)
  div.append(message)
  
  _append(div)
}

function audible_in(sender, url, message, timestamp) {
    var div = $('<div style="clear: both"></div>')
    div.attr('class', 'message audible_in')
    
    _createAudible(div, sender, url, message, timestamp);
}

function audible_out(sender, url, message, timestamp) {
    var div = $('<div style="clear: both"></div>')
    div.attr('class', 'message audible_out')
    
    _createAudible(div, sender, url, message, timestamp);
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