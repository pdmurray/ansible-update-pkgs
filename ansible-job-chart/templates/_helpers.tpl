{{- define "ansible-job-chart.jobSpec" -}}
initContainers:
- name: copy-ssh-key
  image: alpine
  command:
  - sh
  - -c
  - |
    cp /etc/ssh_keys/id_rsa /tmp/id_rsa && chmod 600 /tmp/id_rsa && ls -l /tmp/id_rsa
  volumeMounts:
  - name: ssh-key-volume
    mountPath: /etc/ssh_keys
  - name: temp-volume
    mountPath: /tmp
containers:
- name: ansible-container
  image: {{ .Values.image.repository }}:{{ .Values.image.tag }}
  command: ["/bin/sh", "-c"]
  args: ["ansible-playbook -i /etc/inventory/inventory.ini {{ .Values.playbook.extraArgs }} {{ .Values.playbook.name }}"]
  env:
  {{- if .Values.truenasServers }}
  - name: TRUENAS_CONFIG_FILE
    value: /etc/truenas-config/truenas-servers.yml
  {{- end }}
  volumeMounts:
  - name: temp-volume
    mountPath: /etc/ssh_keys
    readOnly: true
  - name: inventory-volume
    mountPath: /etc/inventory
    readOnly: true
  {{- if .Values.truenasServers }}
  - name: truenas-config-volume
    mountPath: /etc/truenas-config
  {{- end }}
restartPolicy: Never
volumes:
- name: ssh-key-volume
  secret:
    secretName: ansible-ssh-key
- name: inventory-volume
  secret:
    secretName: inventory-secret
- name: temp-volume
  emptyDir: {}
{{- if .Values.truenasServers }}
- name: truenas-config-volume
  secret:
    secretName: truenas-config-secret
{{- end }}
{{- end }}
