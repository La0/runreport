<template>
  <div id="stats">
    <div v-if="stats">
      <h3>Hours & distances</h3>
      <HoursDistance></HoursDistance>

      <h3>Sessions by sports</h3>
      <Sports></Sports>
    </div>
    <div class="alert alert-info" v-else>
      Loading...
    </div>
  </div>
</template>

<script>
module.exports = {
  components : {
    Sports : require('./Sports.vue').default,
    HoursDistance : require('./HoursDistance.vue').default,
  },
  props : {
    user : String,
  },
  mounted: function(){
    // Load stats
    this.$store.dispatch('load_stats', {
      user: this.user,
    });
  },
  computed : {
    stats : function(){
      return this.$store.state.stats;
    },
  },
};
</script>
