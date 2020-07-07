<template>
  <div id="app" class="container-pc">
    <div id="nav">
      <router-link to="/">Upcoming fixtures</router-link> |
      <router-link to="/test">Manual Testing</router-link> |
      <router-link to="/howto">How To Manual</router-link> |
      <router-link to="/market">Odds market</router-link> |
      <router-link to="/team">Team Report</router-link> |
      <router-link to="/visualizer">Data Visualizer</router-link>
    </div>
    <router-view/>
  </div>
</template>


<style lang="scss">
#app {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
}
#nav {
  padding: 30px;
  a {
    font-weight: bold;
    color: #2c3e50;
    &.router-link-exact-active {
      color: #42b983;
    }
  }
}

.container-pc {
  padding-right: 15px;
  padding-left: 15px;
  margin-right: auto;
  margin-left: auto;
}

</style>

<style>
@import 'https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css';
@import '../node_modules/purecss/build/pure-min.css';
@import '../node_modules/purecss/build/grids-responsive-min.css';
</style>
