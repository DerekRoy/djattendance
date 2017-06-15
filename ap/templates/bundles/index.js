/*
 * Base npm struture for entire website
 * Add any libraries that can be installed by npm here.
 *
 * Goal is to have one large javascript file for the entire
 * site. That way we can use caching to our advantage to
 * speed up site load.
 */

/**************************
* expose global libraries *
**************************/
import 'expose-loader?moment!moment'
import 'expose-loader?Countable!countable'
import 'expose-loader?Dropzone!dropzone'; import 'dropzone/dist/dropzone.css'
import 'expose-loader?_!underscore'
import 'expose-loader?xolor!xolor'
import 'expose-loader?fastclick!fastclick'
import 'expose-loader?autosize!autosize/dist/autosize'

/**********************************
* load plugins and respective css *
**********************************/
import './jquery_bootstrap'
import 'fullcalendar'; import 'fullcalendar/dist/fullcalendar.css'
import 'jquery.shorten/src/jquery.shorten'
import 'devbridge-autocomplete'
import 'selectize'; import 'selectize/dist/css/selectize.default.css'
import 'bootstrap-toggle'; import 'bootstrap-toggle/css/bootstrap-toggle.css'
import 'pdfmake/build/pdfmake'
import 'pdfmake/build/vfs_fonts.js'
// Datatables import, see https://datatables.net/forums/discussion/39648/datatable-buttons-not-working-on-webpack
import "datatables.net"
import "datatables.net-bs"; import 'datatables.net-bs/css/dataTables.bootstrap.css'
import "datatables.net-buttons"
import "datatables.net-buttons-bs"; import 'datatables.net-buttons-bs/css/buttons.bootstrap.css'
import 'datatables.net-buttons/js/buttons.colVis'
import 'datatables.net-buttons/js/buttons.html5'
import 'datatables.net-buttons/js/buttons.flash'
import 'datatables.net-buttons/js/buttons.print'
import 'datatables.net-select'; import 'datatables.net-select-bs/css/select.bootstrap.css'
import 'datatables.net-fixedheader'; import 'fullcalendar/dist/fullcalendar.css'
import 'datatables.net-scroller'; import 'datatables.net-scroller-bs/css/scroller.bootstrap.css'
import 'jquery-ui'; import 'jquery-ui/themes/base/all.css'
import 'jquery-ui/ui/widgets/datepicker'
import 'jquery-seat-charts'; import 'jquery-seat-charts/jquery.seat-charts.css'
// select2 js handled by django_select2
import 'select2/dist/css/select2.css'

/******************
* Custom AP files *
******************/
import 'bootflat-ftta/bootflat/scss/bootflat.scss'
import 'ap/css/jquery.autocomplete.css'
import 'ap/css/select2-bootstrap.css'
import 'ap/css/base.css'
import 'ap/css/offcanvas.css'
import 'ap/js/init'
