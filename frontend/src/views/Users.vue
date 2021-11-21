<template>
  <div class="users">
    <h1 class="subtitle-1 grey--text">Users</h1>

    <v-snackbar v-model="snackbar" :timeout="8000" top color="red darken-4">
      <span>An error occurred while connecting to the servers.</span>
      <v-btn text color="white" @click="snackbar = false">Close</v-btn>
    </v-snackbar>

    <v-container class="my-5">
      <v-row wrap>
        <v-tooltip top>
          <template v-slot:activator="{ on }">
            <v-btn small text depressed color="grey--text" @click="sortBy('num_gpus')" v-on="on">
              <v-icon left small>filter_none</v-icon>
              <span class="caption">by number of GPUs</span>
            </v-btn>
          </template>
          <span>Sort users by number of GPUs</span>
        </v-tooltip>

        <v-tooltip top>
          <template v-slot:activator="{ on }">
            <v-btn small text depressed color="grey--text" @click="sortBy('gpu_ram')" v-on="on">
              <v-icon left small>memory</v-icon>
              <span class="caption">by GPU RAM</span>
            </v-btn>
          </template>
          <span>Sort users by GPU RAM</span>
        </v-tooltip>

        <v-spacer></v-spacer>
        <span class="grey--text pr-2 my-2" v-if="date !== ''">Last update: {{ date }}</span>
        <v-btn text color="grey" class="my-0" :loading="refreshLoading" @click="refresh">
          <v-icon left>refresh</v-icon>
          <span>Refresh</span>
        </v-btn>

      </v-row>

      <div class="my-10">
        <v-simple-table dense>
          <thead>
            <tr>
              <td><span class="font-weight-bold">User</span></td>
              <td><span class="font-weight-bold">Number of GPUs</span></td>
              <td><span class="font-weight-bold">GPU RAM</span></td>
            </tr>
          </thead>
          <tbody>
            <tr v-for="user in processList()" :key="user.username">
              <td><span>{{ user.username }}</span></td>
              <td><span>{{ user.num_gpus }}</span></td>
              <td><span>{{ user.gpu_ram }}</span></td>
            </tr>
          </tbody>
        </v-simple-table>
      </div>
    </v-container>

  </div>
</template>

<script>
// @ is an alias to /src
import { HTTP } from './http-common';

export default {
  created() {
    this.refresh();
    this.timer = setInterval(this.refresh, 60000)
  },
  beforeDestroy() {
    clearInterval(this.timer)
  },
  data() {
    return {
      users: [],
      refreshLoading: false,
      onlyShowMyProc: true,
      snackbar: false,
      date: '',
    }
  },
  methods: {
    sortBy(prop) {
      this.users.sort((a, b) => a[prop] > b[prop] ? -1 : 1)
    },
    processList() {
      return this.users
    },
    refresh() {
      this.refreshLoading = true;
      HTTP.get('get-users')
          .then(res => {
            this.users = res.data;
            this.refreshLoading = false;
            this.date = new Date().toLocaleString("de-DE", {timeZone: "Europe/Berlin"});
          })
          .catch(err => {
            console.log(err);
            this.refreshLoading = false;
            this.snackbar = true;
          });
    }
  }
}
</script>