const axios = require('axios');
const _ = require('lodash');
const Vue = require('vue').default;
const Vuex = require('vuex').default;
Vue.use(Vuex);

module.exports = new Vuex.Store({
  state : {
    locale : 'fr-fr',
    stats : null,
  },
  mutations : {
    use_stats : function(state, stats){
      state.stats = _.clone(stats);
    },
  },
  actions : {
    load_stats : function(state, payload){
      var url = '/user/' + payload.user + '/stats/';
      axios.get(url).then(function(resp){
        state.commit('use_stats', resp.data);
      });
    },
  },
});
