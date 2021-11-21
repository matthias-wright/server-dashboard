<template>
  <v-dialog max-width="600px" v-model="dialog">
    <template v-slot:activator="{ on, attrs }">
      <v-btn text depressed v-on="on" v-bind="attrs" class="success">Add new project</v-btn>
    </template>
    <v-card>
      <v-card-title>
        <h2>Add a New Project</h2>
      </v-card-title>
      <v-card-text>
        <v-form class="px-3" ref="form">
          <v-text-field label="Title" v-model="title" prepend-icon="folder" :rules="inputRules"></v-text-field>
          <v-textarea label="Information" v-model="content" prepend-icon="edit" :rules="inputRules"></v-textarea>

          <v-menu>
            <template v-slot:activator="{ on, attrs }">
              <v-text-field :value="formattedDate" v-on="on" v-bind="attrs" prepend-icon="date_range" :rules="inputRules"></v-text-field>
            </template>
            <v-date-picker v-model="due"></v-date-picker>
          </v-menu>

          <v-btn text depressed class="success mx-0 mt-3" @click="submit" :loading="loading">Add project</v-btn>
        </v-form>
      </v-card-text>
    </v-card>
  </v-dialog>
</template>


<script>
import moment from 'moment'
//import db from '@/fb'

export default {
  data() {
    return {
      title: '',
      content: '',
      due: null,
      inputRules: [
          v => v.length >= 3 || 'Minimum length is 3 characters'
      ],
      loading: false,
      dialog: false
    }
  },
  methods: {
    submit() {
      if(this.$refs.form.validate()) {
        this.loading = true;

        const project = {
          title: this.title,
          content: this.content,
          due: this.formattedDate,
          person: 'The Net Ninja',
          status: 'ongoing'
        }
        console.log(project);
        this.loading = false;
        this.dialog = false;
        this.$emit('projectAdded');
        //db.collection('projects').add(project).then(() => {
          //console.log('added to db')
        //})

      }
    },
  }, computed: {
    formattedDate() {
      return this.due ? moment(this.due).format("Do MMMM YYYY") : "";
    }
  }
}
</script>