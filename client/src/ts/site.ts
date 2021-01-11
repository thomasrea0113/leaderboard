import 'bootstrap';
import '../scss/site.scss';

import { loadInitialAsync } from './load-initial';
import { initializeNav } from './nav';

loadInitialAsync();
initializeNav();
