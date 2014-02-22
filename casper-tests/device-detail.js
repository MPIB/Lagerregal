casper.test.comment('Casper+Django integration example');
var helper = require('./djangocasper.js');
helper.scenario('/devices/1',
	function() {
		this.test.assertElementCount("#id_ipaddresses option", 1);
		this.click('a[href="#lending"]');
	}, 
	function() {
		this.test.assertVisible("#lending");
		this.click('a[href="#edit"]');
	}, 
	function() {
		this.test.assertVisible("#edit");
		this.click('a[href="#mail"]');
	}, 
	function() {
		this.test.assertVisible("#mail");
	}
);
casper.on("page.error", function(msg, trace) {
    this.echo("Error: " + msg, "ERROR");
});
casper.verbose = true;
helper.run();