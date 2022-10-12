/* @TODO replace with your variables
 * ensure all variables on this page match your project
 */

export const environment = {
  production: false,
  apiServerUrl: 'http://127.0.0.1:5046', // the running FLASK api server url
  auth0: {
    url: 'fsndmalavcoffee.us', // the auth0 domain prefix
    audience: 'coffeeshop', // the audience set for the auth0 app
    clientId: 'DpbnPAM96ONwNsFFXG1dOzCN7Pzf46kY', // the client id generated for the auth0 app
    callbackURL: 'http://127.0.0.1:8104', // the base url of the running ionic application. 
  }
};
