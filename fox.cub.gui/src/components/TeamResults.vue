<style>

    tr.win {
        background-color: #90EE90;
    }

    tr.draw {
        background-color: #C0C0C0;
    }

    tr.lose {
        background-color: #F08080;
    }

    tr.unselected {
        opacity: 0.4;
    }

    .toggle {
        /* opacity 0 so that it can be read by screen readers */
        opacity: 0;
    }

    .label {
        display: inline-block;
        background: #2c3e50;
        width: 2em;
        height: 1em;
        border-radius: 0.5em;
        position: relative;
        cursor: pointer;
        background: #2c3e50;
    }

    .switch {
        position: absolute;
        width: 0.9em;
        height: 0.9em;
        margin-top: 0.05em;
        margin-left: -0.75em;
        border-radius: 1em;
        background: #c0392b;
        box-shadow: 5px 0px 28px -9px rgba(0, 0, 0, 0.75);
        transition: transform 0.2s ease-in;
    }

    .label .toggle:checked + .switch {
        background: #2ecc71;
        transform: translatex(1em);
        transition: transform 0.2s ease-in;
    }
</style>

<template>
    <table class="pure-table pure-table-bordered">
        <thead>
            <tr>
                <th>
                    <label class="label">
                        <input class="toggle" type="checkbox"
                            v-on:click="toggleHandler($event)" checked/>
                        <span class="switch"></span>
                    </label>
                </th>
                <th>Home Team</th>
                <th>Score</th>
                <th>Away Team</th>
            </tr>
        </thead>
        <tr v-for="g in games"
            :key="g.id"
            v-bind:class="[getResult(g.score_for, g.score_against), isSelected(g)]">

            <td>
                <input type="checkbox" v-model="g.selected">
            </td>
            <td v-if="g.venue == Venue.home"><strong>{{g.team_name}}</strong></td>
            <td v-else>{{g.opponent_name}}</td>

            <td v-if="g.venue == Venue.home">
                {{g.score_for}}<small>({{g.team_data[extra_metric]}})</small> -
                {{g.score_against}}<small>({{g.opponent_data[extra_metric]}})</small>
            </td>
            <td v-else>
                {{g.score_against}}<small>({{g.opponent_data[extra_metric]}})</small> -
                {{g.score_for}}<small>({{g.team_data[extra_metric]}})</small>
            </td>

            <td v-if="g.venue == Venue.home">{{g.opponent_name}}</td>
            <td v-else><strong>{{g.team_name}}</strong>
            </td>
        </tr>
    </table>
</template>

<script>

import {Venue} from '@/models/Game';

export default {
    props: ['games', 'extra_metric'],
    data() {
        return {
            Venue
        }
    },
    methods: {
        getResult(score_for, score_against) {
            if (score_for > score_against) {
                return 'win';
            } else if (score_for == score_against) {
                return 'draw';
            } else {
                return 'lose';
            }
        },
        isSelected(game) {
            return game.selected ? '' : 'unselected';
        },
        toggleHandler(ev) {
            var elmts = this.$el.querySelectorAll("tr.unselected");

            let display = ev.target.checked ? "": "none";
            elmts.forEach(el => el.style.display = display);
        }
    }
}
</script>
