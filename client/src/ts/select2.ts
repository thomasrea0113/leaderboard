import 'select2/dist/js/select2';
import 'select2/dist/css/select2.min.css';

import * as $ from 'jquery';

(() => {
    // right now, will automatically render ALL multiple select boxes as select2 whenever
    // this library is loaded. Might need to relax this and require a class be aplied in the
    // future
    $(function () {
        // build the search query when the apply button is clicked
        $('.filter-apply').on('click', () => {
            const selects = <JQuery<HTMLSelectElement>>$('select[multiple][data-field]');
            if (selects.length !== 0) {
                const params = new URLSearchParams(window.location.search);

                selects.each((_, elm) => {
                    const select = $(elm);
                    const field_exact = <string>select.data('field');
                    const field_in = field_exact.replace('__exact', '__in');
                    const vals = (<string[]>select.val()).map((v) => <string>new URLSearchParams(v).get(field_exact));
                    if (vals.length > 0) params.set(field_in, vals.join(','));
                    else params.delete(field_in);
                });

                window.location.search = params.toString();
            }
        });

        $('select[multiple][data-field]').each((i, elm) => {
            const $this = $(elm);
            const field = <string>$this.data('field');
            const field_in = field.replace('__exact', '__in');
            const params = new URLSearchParams(window.location.search);
            const selected = params
                .get(field_in)
                ?.split(',')
                .map((s) => {
                    const val = new URLSearchParams(window.location.search);
                    val.append(field, s);
                    val.sort();
                    return val.toString();
                });

            if (selected !== undefined && selected.length !== 0) {
                const options = <JQuery<HTMLOptionElement>>$this.children('option');
                options
                    .filter((_, e) => {
                        // TODO it seems redundant and costly to keep creating these URLSearchParams,
                        // but we need to ensure the same sort order for the sake of comparison
                        const params = new URLSearchParams(e.value);
                        params.sort();
                        return selected.includes(params.toString());
                    })
                    .prop('selected', true);
            }
        });

        $('select[multiple]').select2();
    });
})();
