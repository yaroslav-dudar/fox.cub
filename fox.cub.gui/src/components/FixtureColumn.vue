<style lang="scss">
    .fixedbutton {
        position: fixed;
        bottom: 10px;
        right: 10px;
    }

    span.up {
        background-color: #90EE90;
    }

    span.freeze {
        background-color: #C0C0C0;
    }

    span.down {
        background-color: #F08080;
    }
</style>

<template>
    <td>
        {{getName(fixture)}}
        <span v-bind:class="getClass()">{{diff}}</span>
    </td>

</template>

<script>
import {Venue} from '@/models/Game';


export default {
    props: ['fixture', 'venue'],
    created: function() {
        let interm_val = this.venue == Venue.home
            ? this.fixture.homeDiff
            : this.fixture.awayDiff;

        if (!interm_val) this.diff = 1.0;
        this.diff = interm_val.toFixed(2);
    },
    methods: {

        getClass() {
            if (!this.diff) return "freeze";
            if (this.diff > 1.02) return "up";
            if (this.diff < 0.98) return "down";
            return "freeze";
        },

        getName() {
            return this.venue == Venue.home
                ? this.fixture.home_name
                : this.fixture.away_name;
        }
    }
}
</script>