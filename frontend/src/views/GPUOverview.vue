<template>
  <div class="gpu-overview">
    <h1 class="subtitle-1 grey--text">GPU Overview</h1>

    <v-snackbar v-model="snackbar" :timeout="8000" top color="red darken-4">
      <span>An error occurred while connecting to the servers.</span>
      <v-btn text color="white" @click="snackbar = false">Close</v-btn>
    </v-snackbar>

    <v-container class="mb-5">
      <v-row wrap>
        <v-switch class="px-2 my-1 pt-5" @change="switchHighlightFreeGPU()" color="green lighten-2" label="Highlight free GPUs"></v-switch>
        <v-switch class="px-2 my-1 pt-5" @change="switchShowFreeGPU()" color="green lighten-2" label="Only show servers with free GPUs"></v-switch>
        <v-text-field class="px-2 my-1" v-model="username" color="purple" @change="store_username()" label="Type in username to highlight"></v-text-field>
        <v-spacer></v-spacer>
        <span class="grey--text pr-2 my-2 pt-5" v-if="date !== ''">Last update: {{ date }}</span>
        <div class="my-1 pt-4">
          <v-btn text color="grey" :loading="refreshLoading" @click="refresh">
            <v-icon left>refresh</v-icon>
            <span>Refresh</span>
          </v-btn>
        </div>

      </v-row>

      <v-row wrap>
        <v-col class="my-2" cols="12" lg="6" v-for="server in processList()" :key="server.hostname">
          <div class="white">
            <div class="ma-2">
              <span class="grey--text text--darken-3 font-weight-bold">{{ server.hostname }}</span>
              <v-simple-table dense>
                <tbody>
                <tr v-for="gpu in server.gpus" :key="gpu.index" :class="(gpu.memory_used < gpu.memory_total * 0.1) && highlightFreeGPUs ? 'green lighten-4' : 'white'">
                  <td class="pa-0 ma-0"><span class="teal--text text--lighten-1">[{{ gpu.index }}]</span></td>
                  <td class="pa-0 ma-0"><span class="indigo--text text--darken-4">{{ gpu.name }}</span></td>
                  <td class="pa-0 ma-0"><span>| </span></td>
                  <td class="pa-0 ma-0">
                    <span class="red--text text--darken-4" v-if="gpu.temperature_gpu < 50">{{ gpu.temperature_gpu }}'C</span>
                    <span class="deep-orange--text text--accent-3 font-weight-bold" v-if="gpu.temperature_gpu >= 50">{{ gpu.temperature_gpu }}'C</span>,
                  </td>
                  <td class="pa-0 ma-0">
                    <span class="green--text text--darken-4" v-if="gpu.utilization_gpu === 0">{{ gpu.utilization_gpu }}</span>
                    <span class="green--text text--darken-2 font-weight-bold" v-if="gpu.utilization_gpu > 0">{{ gpu.utilization_gpu }}</span>
                  </td>
                  <td>
                    <span class="green--text text--darken-4" v-if="gpu.utilization_gpu === 0">%</span>
                    <span class="green--text text--darken-2 font-weight-bold" v-if="gpu.utilization_gpu > 0">%</span>
                  </td>
                  <td class="pa-0 ma-0"><span>| </span></td>
                  <td class="pa-0 ma-0">
                    <span class="lime--text text--darken-3 font-weight-bold">{{ gpu.memory_used }}</span> /
                    <span class="lime--text text--darken-4">{{ gpu.memory_total }}</span> MB
                  </td>
                  <td class="pa-0 ma-0"><span>| </span></td>
                  <td class="pa-0 ma-0">
                    <div v-if="gpu.processes.length <= maxProcessesShow" class="pa-0 ma-0">
                      <span class="px-1" v-for="process in gpu.processes" :key="process.pid">
                        <span v-if="process.username === username && highlightUsername" class="purple--text">{{ process.username }}</span>
                        <span v-if="process.username !== username || !highlightUsername">{{ process.username }}</span>
                        (<span class="lime--text text--darken-4">{{ process.gpu_memory_usage }}</span>)
                      </span>
                    </div>
                    <div v-if="gpu.processes.length > maxProcessesShow" class="pa-0 ma-0">
                      <span class="px-1" v-for="process in gpu.processes.slice(0, maxProcessesShow)" :key="process.pid">
                        <span v-if="process.username === username && highlightUsername" class="purple--text pa-0 ma-0">{{ process.username }}</span>
                        <span v-if="process.username !== username || !highlightUsername" class="pa-0 ma-0">{{ process.username }}</span>
                        (<span class="lime--text text--darken-4">{{ process.gpu_memory_usage }}</span>)
                      </span>
                      <v-tooltip top content-class="grey">
                        <template v-slot:activator="{ on, attrs }">
                          <v-btn icon v-bind="attrs" v-on="on">
                            <v-icon color="grey darken-3">more_horiz</v-icon>
                          </v-btn>
                        </template>
                        <span class="pa-0 ma-0" v-for="process in gpu.processes" :key="process.pid">
                          <span v-if="process.username === username && highlightUsername" class="purple--text pa-0 ma-0">{{ process.username }}</span>
                          <span v-if="process.username !== username || !highlightUsername" class="pa-0 ma-0">{{ process.username }}</span>
                          (<span class="black--text text--darken-2">{{ process.gpu_memory_usage }}</span>)
                        </span>
                      </v-tooltip>
                    </div>
                  </td>
                </tr>
                </tbody>
              </v-simple-table>
            </div>
          </div>
        </v-col>
      </v-row>
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
      servers: [],
      highlightFreeGPUs: false,
      onlyShowFreeGPU: false,
      highlightUsername: true,
      maxProcessesShow: 1,
      refreshLoading: false,
      snackbar: false,
      date: '',
    }
  },
  methods: {
    switchHighlightFreeGPU() {
      this.highlightFreeGPUs = !this.highlightFreeGPUs;
    },
    switchShowFreeGPU() {
      this.onlyShowFreeGPU = !this.onlyShowFreeGPU;
    },
    store_username() {
      localStorage.setItem('username', this.username);
    },
    processList() {
      let serverList = [...this.servers]

      let serverListFiltered = [];
      if (this.onlyShowFreeGPU) {
        for (let i = 0; i < serverList.length; i++) {
          let foundFreeGPU = false;
          for (let j = 0; j < serverList[i].gpus.length; j++) {
            if (serverList[i].gpus[j].memory_used < (serverList[i].gpus[j].memory_total * 0.1)) {
              foundFreeGPU = true;
              break;
            }
          }
          if (foundFreeGPU) {
            serverListFiltered.push(serverList[i])
          }
        }
      } else {
        serverListFiltered = serverList;
      }
      return serverListFiltered;
    },
    refresh() {
      this.refreshLoading = true;
      HTTP.get('get-gpus')
          .then(res => {
            this.servers = res.data;
            this.servers.sort((a, b) => a.hostname < b.hostname ? -1 : 1);
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