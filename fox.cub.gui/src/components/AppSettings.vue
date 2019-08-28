<style lang="scss">
.fixedbutton {
    position: fixed;
    bottom: 10px;
    right: 10px;
}
</style>

<template>
    <div>
        <button class="pure-button fixedbutton" v-on:click="openModel">
            <i class="fa fa-cog"></i>
            Settings
        </button>
        <modal name="appSettings" >
            <form class="pure-form pure-form-stacked container">
                <legend>Application settings</legend>
                <label for="full_history" class="pure-checkbox">
                    <input id="full_history"
                        type="checkbox"
                        v-model="settings.full_history">
                        Show full history of games
                </label>

                <label for="trendSize">Trend size</label>
                <select id="trendSize" v-model="settings.rolling_trend.size" class="form-control pure-input-1-2">
                    <option value="6">6 games trend</option>
                    <option value="10">10 games trend</option>
                </select>

                <label for="trendType">Trend type</label>
                <select id="trendType" v-model="settings.rolling_trend.type" class="form-control pure-input-1-2">
                    <option value="xG">Expected goals Ingogol</option>
                    <option value="goals">Actual goals</option>
                </select>

                <label for="trendType">Games Filter</label>
                <select id="trendType" v-model="settings.away_home_filter" class="form-control pure-input-1-2">
                    <option v-bind:value="true">Home - Away games only</option>
                    <option v-bind:value="false">Show all games</option>
                </select>

                <button class="pure-button" v-on:click="resetFilters">
                    Reset Selected Games
                </button>
            </form>

        </modal>
    </div>
</template>

<script>
import Vue from 'vue'
import vmodal from 'vue-js-modal'
Vue.use(vmodal)

export default {
    props: ['settings'],
    methods: {
        openModel() { this.$modal.show('appSettings'); },
        resetFilters() { this.$emit('reset'); }
    }
}
</script>
