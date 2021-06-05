const fs = require('fs')

const REG_GROUP = /^\s*\[(.+?)\]\s*$/
const REG_PROP = /^\s*([^#].*?)\s*=\s*(.*?)\s*$/

function parse(string) {
	var object = {}
	var lines = string.split('\n')
	var group
	var match

	for(let i = 0, len = lines.length; i !== len; i++){
		if(match = lines[i].match(REG_GROUP))
			object[match[1]] = group = object[match[1]] || {};
		else if(group && (match = lines[i].match(REG_PROP)))
			group[match[1]] = match[2];
	}

	return object;
}

function parseFile(file, callback){
	fs.readFile(file, 'utf-8', function(error, data){
		if(error)
			return callback(error);

		callback(null, parse(data))
	})
}

module.exports = {
  parseFile,
}
