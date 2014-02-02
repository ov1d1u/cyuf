var hide_timestamp = true;

String.prototype.endsWith = function(pattern) {
    var d = this.length - pattern.length;
    return d >= 0 && this.lastIndexOf(pattern) === d;
};

function baseName(str)
{
   var base = new String(str).substring(str.lastIndexOf('/') + 1); 
   return base;
}

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

function _bytesToSize(bytes) {
   var sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
   if (bytes == 0) return '0 Bytes';
   var i = parseInt(Math.floor(Math.log(bytes) / Math.log(1024)));
   return Math.round(bytes / Math.pow(1024, i), 2) + ' ' + sizes[i];
};

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

function file_in(sender, files, sizes, transfer_id, icon) {
    files = $.parseJSON(files)
    sizes = $.parseJSON(sizes)
    var div = $('<div></div>')
    div.attr('class', 'file_in')
    div.attr('id', transfer_id)
    
    var imagediv = $('<div></div')
    imagediv.attr('class', 'file_in_icon')
    imagediv.html('<img src="data:image/png;base64,' + icon + '"></img>')
    div.append(imagediv)
    
    var is_images = true;
    var file_types;
    
    for (filename in files) {
	if (!files[filename].endsWith('.jpg') || !files[filename].endsWith('.jpeg') ||
	  !files[filename].endsWith('.gif') || !files[filename].endsWith('.png'))
	  is_images = false;
    }
    
    if (is_images) {
      if (files.length == 1) {
	file_types = 'photo';
      } else {
	file_types = 'photos';
      }
    } else {
      if (files.length == 1) {
	file_types = 'file';
      } else {
	file_types = 'files';
      }
    }
    
    var textdiv = $('<div></div>')
    textdiv.attr('class', 'file_in_text')
    textdiv.html('<span style="color: #77714a;"><b>' +
	     sender + ' is sending you ' + files.length + ' ' + file_types + ':</b></span> ')
    
    for (x = 0; x < files.length; x++) {
	textdiv.html(textdiv.html() + files[x] + ' (' + _bytesToSize(sizes[x]) + ')' + '<br/>')
	if (x > 5) {
	    total_size = 0
	    for (i in sizes) total_size += parseInt(sizes[i]);
	    textdiv.html(textdiv.html() + '<img src="res/arrow-right.png" onclick="javascript:hide_expand_ft(\'' + transfer_id + '\')"' +
			 'id="arrow_' + transfer_id + '" class="arrow_not_toggled" alt=""/>' + 'and ' + (files.length - 5) +
			 ' others. (' + _bytesToSize(total_size) + ' total) <br/>')
	    var morediv = $('<div></div>')
	    morediv.attr('id', 'transfer_more_' + transfer_id)
	    morediv.css('display', 'none')
	    for (y = 5; y < files.length; y++) {
		morediv.html(morediv.html() + files[y] + ' (' + _bytesToSize(sizes[y]) + ')' + '<br/>')
	    }
	    textdiv.append(morediv)
	    break;
	}
    }
    
    if (files.length == 1) {
	textdiv.html(textdiv.html() + '<b><a href="cyuf://save/' + transfer_id + '">Save...</a></b> (Alt+Shift+A) &nbsp;&nbsp;')
	textdiv.html(textdiv.html() + '<b><a href="cyuf://decline/' + transfer_id + '">Decline</a></b> (Alt+Shift+D)')
    } else {
	textdiv.html(textdiv.html() + '<b><a href="cyuf://save/' + transfer_id + '">Save All...</a></b> (Alt+Shift+A) &nbsp;&nbsp;')
	textdiv.html(textdiv.html() + '<b><a href="cyuf://decline/' + transfer_id + '">Decline All</a></b> (Alt+Shift+D)')
    }
    
    div.append(textdiv)
    
    _append(div)
}

function file_cancel(sender, transfer_id) {
    transfer_id = transfer_id.replace(/=/g, '\\=')
    $('#' + transfer_id).attr('class', 'infobox')
    $('#' + transfer_id + ' .file_in_text').html('<b>' + sender + ' has cancelled the file transfer</b>')
    $('#' + transfer_id).append($('<div></div>').css('clear', 'both'))
}

function file_decline(sender, transfer_id) {
    transfer_id = transfer_id.replace(/=/g, '\\=')
    $('#' + transfer_id).attr('class', 'infobox')
    $('#' + transfer_id + ' .file_in_text').html('<b>You have declined the file(s) sent by ' + sender + '</b>')
    $('#' + transfer_id).append($('<div></div>').css('clear', 'both'))
}

function file_rejected(sender, transfer_id) {
    transfer_id = transfer_id.replace(/=/g, '\\=')
    $('#' + transfer_id).attr('class', 'infobox')
    $('#' + transfer_id + ' .file_in_text').html('<b>' + sender + ' has declined your file transfer.</b>')
    $('#' + transfer_id).append($('<div></div>').css('clear', 'both'))
}

function cancel_send(sender, transfer_id) {
    transfer_id = transfer_id.replace(/=/g, '\\=')
    $('#' + transfer_id).attr('class', 'infobox')
    $('#' + transfer_id + ' .file_in_text').html('<b>You have canceled the file transfer.</b>')
    $('#' + transfer_id).append($('<div></div>').css('clear', 'both'))
}

function hide_expand_ft(transfer_id) {
    transfer_id = transfer_id.replace(/=/g, '\\=')
    $('#transfer_more_' + transfer_id).toggle()
    var arrow = $('#arrow_' + transfer_id)
    if (arrow.attr('class') == 'arrow_not_toggled') {
	arrow.attr('class', 'arrow_toggled')
	arrow.attr('src', 'res/arrow-down.png')
    } else {
	arrow.attr('class', 'arrow_not_toggled')
	arrow.attr('src', 'res/arrow-right.png')
    }
}

function file_progress(transfer_id, filename, progress) {
    transfer_id = transfer_id.replace(/=/g, '\\=')
    $('#' + transfer_id).attr('class', 'infobox')
    $('#' + transfer_id + ' .file_in_text').html(
      filename + '<br/>\
      <p><progress value="' + progress + '" max="100" style="height: 12px;"></progress> \
      <b><a href="cyuf://cancel/' + transfer_id + '">Cancel</a></b> (Alt+Shift+C)</p>\
      <div styke="clear: both;"></div>'
    )
}

function transfer_finished(transfer_id, sender, count, action, path) {
    transfer_id = transfer_id.replace(/=/g, '\\=')
    
    if (action == 'open-dir') {
        $('#' + transfer_id).attr('class', 'infobox')
        $('#' + transfer_id + ' .file_in_text').html(
            '<b>You have received ' + count + ' files from ' + sender + '.</b><br/>' +
            '<b><a href="cyuf://open-dir/' + path + '">Reveal files</a></b>'
            )
        $('#' + transfer_id).append($('<div></div>').css('clear', 'both'))
    } else if (action == 'open-file') {
        var is_photo = false;
        
        if (path.endsWith('.jpg') || path.endsWith('.jpeg') ||
          path.endsWith('.gif') || path.endsWith('.png')) {
            is_photo = true;
          }
        
        $('#' + transfer_id).attr('class', 'infobox')
        if (is_photo) {
            $('#' + transfer_id + ' .file_in_text').html(
            '<span class="file_status_text">You have received ' + count + ' photo from ' + sender + '.</span><br/>' +
            '<span class="standard_text_color">' + baseName(path) + '</span><br/>' +
            '<b><a href="cyuf://open-file/' + path + '">Open photo</a></b>'
            )
        } else {
            $('#' + transfer_id + ' .file_in_text').html(
            '<span class="file_status_text">You have received ' + count + ' file from ' + sender + '.</span><br/>' +
            '<span class="standard_text_color">' + baseName(path) + '</span><br/>' +
            '<b><a href="cyuf://open-file/' + path + '">Open file</a></b>'
            )
        }
        $('#' + transfer_id).append($('<div></div>').css('clear', 'both'))
    } else if (action == 'file-sent') {
        var is_photo = false;
        
        if (path.endsWith('.jpg') || path.endsWith('.jpeg') ||
          path.endsWith('.gif') || path.endsWith('.png')) {
            is_photo = true;
          }
        
        $('#' + transfer_id).attr('class', 'infobox')
        if (is_photo) {
            $('#' + transfer_id + ' .file_in_text').html(
            '<span class="file_status_text">You sent ' + count + ' photo to ' + sender + '.</span><br/>' +
            '<span class="standard_text_color">' + baseName(path) + '</span><br/>' +
            '<b><a href="cyuf://open-file/' + path + '">Open photo</a></b>'
            )
        } else {
            $('#' + transfer_id + ' .file_in_text').html(
            '<span class="file_status_text">You have received ' + count + ' file from ' + sender + '.</span><br/>' +
            '<span class="standard_text_color">' + baseName(path) + '</span><br/>' +
            '<b><a href="cyuf://open-file/' + path + '">Open file</a></b>'
            )
        }
    }
}

function file_out(receiver, files, sizes, transfer_id, icon) {
    files = $.parseJSON(files)
    sizes = $.parseJSON(sizes)
    var div = $('<div></div>')
    div.attr('class', 'file_in')
    div.attr('id', transfer_id)
    
    var imagediv = $('<div></div')
    imagediv.attr('class', 'file_in_icon')
    imagediv.html('<img src="data:image/png;base64,' + icon + '"></img>')
    div.append(imagediv)
    
    var textdiv = $('<div></div>')
    textdiv.attr('class', 'file_in_text')
    textdiv.html('<p style="color: #77714a; line-height:30%;"><b>' +
	     'Waiting for ' + receiver + ' to accept ' + files.length + ' file(s):</b></p>')
    
    for (x = 0; x < files.length; x++) {
	textdiv.html(textdiv.html() + files[x] + ' (' + _bytesToSize(sizes[x]) + ')' + '<br/>')
	if (x > 5) {
	    total_size = 0
	    for (i in sizes) total_size += parseInt(sizes[i]);
	    textdiv.html(textdiv.html() + '<img src="res/arrow-right.png" onclick="javascript:hide_expand_ft(\'' + transfer_id + '\')"' +
			 'id="arrow_' + transfer_id + '" class="arrow_not_toggled" alt=""/>' + 'and ' + (files.length - 5) +
			 ' others. (' + _bytesToSize(total_size) + ' total) <br/>')
	    var morediv = $('<div></div>')
	    morediv.attr('id', 'transfer_more_' + transfer_id)
	    morediv.css('display', 'none')
	    for (y = 5; y < files.length; y++) {
		morediv.html(morediv.html() + files[y] + ' (' + _bytesToSize(sizes[y]) + ')' + '<br/>')
	    }
	    textdiv.append(morediv)
	    break;
	}
    }
    
    textdiv.html(textdiv.html() + '<b><a href="cyuf://cancel-send/' + transfer_id + '">Cancel</a></b> (Alt+Shift+C) &nbsp;&nbsp;')
    
    div.append(textdiv)
    
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