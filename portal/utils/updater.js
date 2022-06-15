const { exec } = require("child_process");
const {createHmac, timingSafeEqual} = require("crypto");

const logger = require("./logger")

const compare_signature = (secret, signature, payload) => {
	const hmac = createHmac('sha256', secret=secret)
	hmac.update(payload);
	const new_signature = `sha256=${hmac.digest('hex')}`;
	return (timingSafeEqual(Buffer.from(signature), Buffer.from(new_signature)));
}

const pull_and_restart = () => {
	logger.info("Git Pulling...");
	exec("git pull", (error, stdout, stderr)=>{
		if(error){
			logger.error(`Git Pull errored: ${error}`);
		} else {
			logger.info("Restarting using systemctl...");
			exec("sudo systemctl restart casbot.target");
		}
	});
}

module.exports = {
	compare_signature,
	pull_and_restart
}
