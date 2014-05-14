module.exports = (grunt) ->
  grunt.initConfig
    pkg: grunt.file.readJSON('package.json')
    sass:
      dist:
        options:
          bundleExec: true
          sourcemap: true
        files:
          'example_project/static/css/tx_lobbying.css': 'example_project/static/sass/tx_lobbying.sass'
    jshint:
      all: [
        'example_project/static/js_src/**/*.js'
      ]
    concat:
      app:
        src: [
          'example_project/static/js_src/**/*.js'
          # trick grunt into adding main.js last
          '!example_project/static/js_src/main.js'
          'example_project/static/js_src/main.js'
        ]
        dest: 'example_project/static/js/tx_lobbying.js'
    uglify:
      app:
        files:
          'example_project/static/js/tx_lobbying.min.js': ['<%= concat.app.dest %>']
    watch:
      # use live reload if the browser has it
      # if you don't have it you can get it here:
      # http://feedback.livereload.com/knowledgebase/articles/86242-how-do-i-install-and-use-the-browser-extensions-
      options:
        livereload: true
      sass:
        files: ['example_project/static/sass/**/*.sass']
        tasks: ['sass']
        options:
          livereload: false
          # spawn has to be on or else the css watch won't catch changes
          spawn: true
      css:
        files: ['example_project/static/css/**/*.css']
        options:
          spawn: false
      scripts:
        files: ['example_project/static/js_src/**/*.js']
        tasks: ['concat', 'uglify']
        options:
          spawn: false

  grunt.loadNpmTasks 'grunt-contrib-sass'
  grunt.loadNpmTasks 'grunt-contrib-jshint'
  grunt.loadNpmTasks 'grunt-contrib-concat'
  grunt.loadNpmTasks 'grunt-contrib-uglify'
  grunt.loadNpmTasks 'grunt-contrib-watch'

  # build the assets needed
  grunt.registerTask('build', ['sass', 'concat', 'uglify'])
  # build the assets with sanity checks
  grunt.registerTask('default', ['sass', 'jshint', 'concat', 'uglify'])
  # build assets and automatically re-build when a file changes
  grunt.registerTask('dev', ['build', 'watch'])
