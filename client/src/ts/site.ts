import 'bootstrap';
import '../scss/site.scss';

import { loadInitialAsync } from './load-initial';

loadInitialAsync();

document.getElementById('sidebarCollapse')?.addEventListener('click', () => {
  document.getElementById('sidebar')?.classList.toggle('active');
});
