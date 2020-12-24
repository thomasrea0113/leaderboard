import 'select2/dist/js/select2';
import 'select2/dist/css/select2.min.css';
// eslint-disable-next-line @typescript-eslint/no-var-requires
import * as $ from 'jquery';

// right now, will automatically render ALL multiple select boxes as select2 whenever
// this library is loaded. Might need to relax this and require a class be aplied in the
// future
$(function () {
    $('select[multiple]').select2();
});
