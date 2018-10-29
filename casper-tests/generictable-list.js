casper.test.comment('Casper+Django integration example');
var helper = require('./djangocasper.js');
helper.scenario('/' + casper.cli.options['basename'] + '/',
    function() {
        this.test.assertElementCount("table tr", 31, "Correct amount of elements in list");
        this.test.assertExists('.pager', 'Pagination found');
        this.evaluate(function() {
            $('.pageselect').val(2).change()
            return true;
        });
    },
    function() {
        helper.assertAbsUrl('/' + casper.cli.options['basename'] + '/page/2/sorting/name/filter/');
        this.test.assertElementCount("table tr", 11, "Correct amount of elements in list");
        this.evaluate(function() {
            $('#id_filterstring').val("abc").change()
            return true;
        });
    },
    function() {
        helper.assertAbsUrl('/' + casper.cli.options['basename'] + '/sorting/name/filter/abc');
        this.evaluate(function() {
            $('#id_viewsorting').val("id").change()
            return true;
        });
    },
    function() {
        helper.assertAbsUrl('/' + casper.cli.options['basename'] + '/sorting/id/filter/abc');
    }
);
casper.on("page.error", function(msg, trace) {
    this.echo("Error: " + msg, "ERROR");
});
helper.run();