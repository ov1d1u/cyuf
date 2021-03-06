# Emotions mapping
from collections import OrderedDict

_emotes = {
	':))' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/21.gif',
	':-))' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/21.gif',
	':((' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/20.gif',
	':-((' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/20.gif',
	'O:)' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/25.gif',
	':)>-' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/67.gif',
	':>' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/15.gif',
	':?' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/39.gif',
	'8-|' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/29.gif',
	'8-}' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/35.gif',
	':-|' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/22.gif',
	'>:D<' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/6.gif',
	'(:|' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/37.gif',
	':O)' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/34.gif',
	'**==' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/55.gif',
	':<' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/46.gif',
	':!!' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/110.gif',
	':O3' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/108.gif',
	'~:>' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/52.gif',
	':*' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/11.gif',
	':&' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/31.gif',
	'@)' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/43.gif',
	'I-)' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/28.gif',
	':-W' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/45.gif',
	':"' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/65.gif',
	':-"' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/65.gif',
	':-X' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/8.gif',
	'X(' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/14.gif',
	':)]' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/100.gif',
	'8-X' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/59.gif',
	':-P' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/10.gif',
	':-Q' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/112.gif',
	'%%-' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/54.gif',
	':-S' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/17.gif',
	':-T' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/104.gif',
	':BD' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/113.gif',
	'=P~' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/38.gif',
	'\M/' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/111.gif',
	':-H' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/103.gif',
	'^:)^' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/77.gif',
	':BZ' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/115.gif',
	':-L' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/62.gif',
	':-O' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/13.gif',
	':-@' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/76.gif',
	':-B' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/26.gif',
	'~X(' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/102.gif',
	':-D' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/4.gif',
	'>:P' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/47.gif',
	'I)' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/28.gif',
	'8->' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/105.gif',
	':|' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/22.gif',
	'L-)' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/30.gif',
	':-<' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/46.gif',
	'O->' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/72.gif',
	':->' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/15.gif',
	':-?' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/39.gif',
	'/:)' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/23.gif',
	':ar!' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons/pirate_2.gif',
	'%-(' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/107.gif',
	';-))' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/71.gif',
	'$)' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/64.gif',
	'(:-|' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/37.gif',
	':-*' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/11.gif',
	'@};-' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/53.gif',
	':SS' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/42.gif',
	':-SS' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/42.gif',
	'#O' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/40.gif',
	'~O)' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/57.gif',
	'X_X' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/109.gif',
	':-&' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/31.gif',
	'[-X' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/68.gif',
	'(*)' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/79.gif',
	':-C' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/101.gif',
	':X' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/8.gif',
	'<:-P' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/36.gif',
	':T' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/104.gif',
	':S' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/17.gif',
	':P' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/10.gif',
	'#:S' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/18.gif',
	'\:-D/' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/69.gif',
	':O' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/13.gif',
	':L' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/62.gif',
	'\:D/' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/69.gif',
	':J' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/78.gif',
	':H' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/103.gif',
	':W' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/45.gif',
	':D' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/4.gif',
	'@-)' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/43.gif',
	':B' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/26.gif',
	':C' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/101.gif',
	':@' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/76.gif',
	':-??' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/106.gif',
	'=((' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/12.gif',
	'3:O' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/50.gif',
	'[X' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/68.gif',
	'8>' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/105.gif',
	'<:P' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/36.gif',
	':-J' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/78.gif',
	'%(' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/107.gif',
	';;)' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/5.gif',
	'[..]' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons/transformers.gif',
	'<):)' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/48.gif',
	'#:-S' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/18.gif',
	'(~~)' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/56.gif',
	':/' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/7.gif',
	'>:-P' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/47.gif',
	'O:-)' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/25.gif',
	':Q' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/112.gif',
	'(%)' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/75.gif',
	':$' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/32.gif',
	'B(' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/66.gif',
	'B)' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/16.gif',
	'=D>' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/41.gif',
	'O=>' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/73.gif',
	':-BZ' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/115.gif',
	';;-)' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/5.gif',
	'=;' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/27.gif',
	'O-+' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/74.gif',
	':-BD' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/113.gif',
	':-/' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/7.gif',
	'B-(' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/66.gif',
	'B-)' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/16.gif',
	'*-:)' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/58.gif',
	'L)' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/30.gif',
	'=))' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/24.gif',
	'~X-(' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/102.gif',
	'8|' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/29.gif',
	'8}' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/35.gif',
	':@)' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/49.gif',
	'=:)' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/60.gif',
	'[-(' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/33.gif',
	':(|)' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/51.gif',
	'x(' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/14.gif',
	'>:/' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/70.gif',
	'>:)' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/19.gif',
	'$-)' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/64.gif',
	';))' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/71.gif',
	'8X' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/59.gif',
	'[-O<' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/63.gif',
	':-$' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/32.gif',
	'^#(^' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/114.gif',
	'>:-/' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/70.gif',
	'>:-)' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/19.gif',
	':??' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/106.gif',
	'3:-O' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/50.gif',
	':">' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/9.gif',
	'#-O' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/40.gif',
	'[(' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/33.gif',
	'/:-)' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/23.gif',
	':^O' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/44.gif',
	'^:-)^' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/77.gif',
	'>:-D<' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/6.gif',
	'>-)' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/61.gif',
	':(' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/2.gif',
	':)' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/1.gif',
	':-)' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/1.gif',
	':-(' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/2.gif',
	';)' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/3.gif',
	';-)' : 'http://l.yimg.com/us.yimg.com/i/mesg/emoticons7/3.gif',
}

emotes = OrderedDict(sorted(_emotes.items(), key=lambda t: -len(t[0])))