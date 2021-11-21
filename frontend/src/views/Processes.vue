<template>
  <div class="processes">
    <h1 class="subtitle-1 grey--text">Processes</h1>

    <v-snackbar v-model="snackbar" :timeout="8000" top color="red darken-4">
      <span>An error occurred while connecting to the servers.</span>
      <v-btn text color="white" @click="snackbar = false">Close</v-btn>
    </v-snackbar>

    <v-container class="my-5">
      <v-row wrap>
        <v-switch class="px-2 my-1 pt-5" @change="switchMyProc()" color="primary" label="Only show my processes"></v-switch>
        <v-text-field class="px-2 my-1" v-model="username" color="purple" @change="store_username()" label="Type in username to filter"></v-text-field>
        <v-spacer></v-spacer>
        <span class="grey--text pr-2 my-2" v-if="date !== ''">Last update: {{ date }}</span>
        <div class="my-1 pt-4">
          <v-btn text color="grey" class="my-0" :loading="refreshLoading" @click="refresh">
            <v-icon left>refresh</v-icon>
            <span>Refresh</span>
          </v-btn>
        </div>

      </v-row>

      <div class="my-5">
        <v-simple-table dense>
          <thead>
            <tr>
              <td><span class="font-weight-bold">Server</span></td>
              <td><span class="font-weight-bold">User</span></td>
              <td><span class="font-weight-bold">PID</span></td>
              <td><span class="font-weight-bold">CPU</span></td>
              <td><span class="font-weight-bold">Memory</span></td>
              <td><span class="font-weight-bold">Start</span></td>
              <td><span class="font-weight-bold">Time</span></td>
              <td><span class="font-weight-bold">Command</span></td>
            </tr>
          </thead>
          <tbody>
            <tr v-for="process in processList()" :key="process.pid">
              <td><span>{{ process.server }}</span></td>
              <td>
                <span v-if="process.user === username" class="purple--text">{{ process.user }}</span>
                <span v-if="process.user !== username">{{ process.user }}</span>
              </td>
              <td><span>{{ process.pid }}</span></td>
              <td><span>{{ process.cpu }}%</span></td>
              <td><span>{{ process.mem }}%</span></td>
              <td><span>{{ process.start }}</span></td>
              <td><span>{{ process.time }}</span></td>
              <td><span>{{ process.command }}</span></td>
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
      username: localStorage.getItem('username'),
      processes: [],
      refreshLoading: false,
      onlyShowMyProc: false,
      snackbar: false,
      date: '',
    }
  },
  methods: {
    switchMyProc() {
      this.onlyShowMyProc = !this.onlyShowMyProc;
    },
    store_username() {
      localStorage.setItem('username', this.username);
    },
    processList() {
      let processListFiltered = [];
      if (this.onlyShowMyProc) {
        for (let i = 0; i < this.processes.length; i++) {
          if (this.processes[i].user === this.username) {
            processListFiltered.push(this.processes[i]);
          }
        }
      } else {
        processListFiltered = this.processes;
      }
      return processListFiltered;
    },
    refresh() {
      this.refreshLoading = true;
      HTTP.get('get-processes')
          .then(res => {
            this.processes = res.data;
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