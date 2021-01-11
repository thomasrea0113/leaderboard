/**
 * a simple function to attach the 'transitioning' class to the nav, which
 * disable pointer events during a transition
 */
export const initializeNav = (): void => {
  document.querySelectorAll('.dropdown').forEach((dropDown) =>
    dropDown.addEventListener('mouseenter', () =>
      dropDown.querySelectorAll('.dropdown-menu').forEach((menu) => {
        menu.classList.add('transitioning');
        console.log('adding transition');
      }),
    ),
  );

  document.querySelectorAll('.dropdown-menu').forEach((menu) =>
    menu.addEventListener('transitionend', () => {
      console.log('removing transition');
      return menu.classList.remove('transitioning');
    }),
  );
};
